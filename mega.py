import re
import json
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util import Counter
import os
import random
import binascii
import requests
import errors
from crypto import *

class Mega(object):

    def __init__(self):
        self.schema = 'https'
        self.domain = 'mega.co.nz'
        self.timeout = 160 #max time (secs) to wait for response from api requests
        self.sid = None
        self.sequence_num = random.randint(0, 0xFFFFFFFF)

    @classmethod
    def login(class_, email, password):
        inst = class_()
        inst.login_user(email, password)
        return inst


    def login_user(self, email, password):
        password_aes = prepare_key(str_to_a32(password))
        uh = stringhash(email, password_aes)
        resp = self.api_request({'a': 'us', 'user': email, 'uh': uh})
        #if numeric error code response
        if isinstance(resp, int):
            raise errors.RequestError(resp)
        self._login_process(resp, password_aes)


    def _login_process(self, resp, password):
        encrypted_master_key = base64_to_a32(resp['k'])
        self.master_key = decrypt_key(encrypted_master_key, password)
        if 'tsid' in resp:
            tsid = base64_url_decode(resp['tsid'])
            key_encrypted = a32_to_str(
                encrypt_key(str_to_a32(tsid[:16]), self.master_key))
            if key_encrypted == tsid[-16:]:
                self.sid = resp['tsid']
        elif 'csid' in resp:
            encrypted_rsa_private_key = base64_to_a32(resp['privk'])
            rsa_private_key = decrypt_key(encrypted_rsa_private_key, self.master_key)

            private_key = a32_to_str(rsa_private_key)
            self.rsa_private_key = [0, 0, 0, 0]

            for i in range(4):
                l = ((ord(private_key[0]) * 256 + ord(private_key[1]) + 7) / 8) + 2
                self.rsa_private_key[i] = mpi_to_int(private_key[:l])
                private_key = private_key[l:]

            encrypted_sid = mpi_to_int(base64_url_decode(resp['csid']))
            rsa_decrypter = RSA.construct(
                (self.rsa_private_key[0] * self.rsa_private_key[1],
                 0L, self.rsa_private_key[2], self.rsa_private_key[0],
                 self.rsa_private_key[1]))

            sid = '%x' % rsa_decrypter.key._decrypt(encrypted_sid)
            sid = binascii.unhexlify('0' + sid if len(sid) % 2 else sid)
            self.sid = base64_url_encode(sid[:43])

    def api_request(self, data):
        params = {'id': self.sequence_num}
        self.sequence_num += 1

        if self.sid:
            params.update({'sid': self.sid})
        req = requests.post(
            '{0}://g.api.{1}/cs'.format(self.schema,self.domain), params=params, data=json.dumps([data]), timeout=self.timeout)
        json_resp = req.json()
        #if numeric error code response
        if isinstance(json_resp, int):
            raise errors.RequestError(json_resp)
        return json_resp[0]

    def get_files(self):
        files = self.api_request({'a': 'f', 'c': 1})
        files_dict = {}
        for file in files['f']:
            files_dict[file['h']] = self.process_file(file)
        return files_dict


    def download_url(self, url):
        path = self.parse_url(url).split('!')
        file_id = path[0]
        file_key = path[1]
        self.download_file(file_id, file_key, is_public=True)

    def parse_url(self, url):
        #parse file id and key from url
        if('!' in url):
            match = re.findall(r'/#!(.*)', url)
            path = match[0]
            return path
        else:
            raise errors.RequestError('Url key missing')

    def download_file(self, file_id, file_key, is_public=False):
        if is_public:
            file_key = base64_to_a32(file_key)
            file_data = self.api_request({'a': 'g', 'g': 1, 'p': file_id})
        else:
            file_data = self.api_request({'a': 'g', 'g': 1, 'n': file_id})

        k = (file_key[0] ^ file_key[4], file_key[1] ^ file_key[5],
             file_key[2] ^ file_key[6], file_key[3] ^ file_key[7])
        iv = file_key[4:6] + (0, 0)
        meta_mac = file_key[6:8]

        file_url = file_data['g']
        file_size = file_data['s']
        attribs = base64_url_decode(file_data['at'])
        attribs = decrypt_attr(attribs, k)
        file_name = attribs['n']

        input_file = requests.get(file_url, stream=True).raw
        output_file = open(file_name, 'wb')

        counter = Counter.new(
            128, initial_value=((iv[0] << 32) + iv[1]) << 64)
        aes = AES.new(a32_to_str(k), AES.MODE_CTR, counter=counter)

        file_mac = (0, 0, 0, 0)
        for chunk_start, chunk_size in sorted(get_chunks(file_size).items()):
            chunk = input_file.read(chunk_size)
            chunk = aes.decrypt(chunk)
            output_file.write(chunk)

            chunk_mac = [iv[0], iv[1], iv[0], iv[1]]
            for i in range(0, len(chunk), 16):
                block = chunk[i:i+16]
                if len(block) % 16:
                    block += '\0' * (16 - (len(block) % 16))
                block = str_to_a32(block)
                chunk_mac = [
                    chunk_mac[0] ^ block[0],
                    chunk_mac[1] ^ block[1],
                    chunk_mac[2] ^ block[2],
                    chunk_mac[3] ^ block[3]]
                chunk_mac = aes_cbc_encrypt_a32(chunk_mac, k)

            file_mac = [
                file_mac[0] ^ chunk_mac[0],
                file_mac[1] ^ chunk_mac[1],
                file_mac[2] ^ chunk_mac[2],
                file_mac[3] ^ chunk_mac[3]]
            file_mac = aes_cbc_encrypt_a32(file_mac, k)
        output_file.close()

        # check mac integrity
        if (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3]) != meta_mac:
            raise ValueError('Mismatched mac')

    def get_public_url(self, file_id, file_key):
        if file_id and file_key:
            public_handle = self.api_request({'a': 'l', 'n': file_id})
            decrypted_key = a32_to_base64(file_key)
            return '{0}://{1}/#!%s!%s'.format(self.schema, self.domain) % (public_handle, decrypted_key)
        else:
            raise errors.ValidationError('File id and key must be set')

    def upload(self, filename, dest=None):
        #determine storage node
        if dest is None:
            #if none set, upload to cloud drive node
            root_id = getattr(self, 'root_id')
            if root_id is None:
                self.get_files()
            dest = self.root_id

        #request upload url, call 'u' method
        input_file = open(filename, 'rb')
        size = os.path.getsize(filename)
        ul_url = self.api_request({'a': 'u', 's': size})['p']

        #generate random aes key (128) for file
        ul_key = [random.randint(0, 0xFFFFFFFF) for r in range(6)]
        count = Counter.new(128, initial_value=((ul_key[4] << 32) + ul_key[5]) << 64)
        aes = AES.new(a32_to_str(ul_key[:4]), AES.MODE_CTR, counter=count)

        file_mac = [0, 0, 0, 0]
        for chunk_start, chunk_size in sorted(get_chunks(size).items()):
            chunk = input_file.read(chunk_size)

            #determine chunks mac
            chunk_mac = [ul_key[4], ul_key[5], ul_key[4], ul_key[5]]
            for i in range(0, len(chunk), 16):
                block = chunk[i:i+16]
                if len(block) % 16:
                    block += '\0' * (16 - len(block) % 16)
                block = str_to_a32(block)
                chunk_mac = [chunk_mac[0] ^ block[0], chunk_mac[1] ^ block[1], chunk_mac[2] ^ block[2],
                             chunk_mac[3] ^ block[3]]
                chunk_mac = aes_cbc_encrypt_a32(chunk_mac, ul_key[:4])

            #our files mac
            file_mac = [file_mac[0] ^ chunk_mac[0], file_mac[1] ^ chunk_mac[1], file_mac[2] ^ chunk_mac[2],
                        file_mac[3] ^ chunk_mac[3]]
            file_mac = aes_cbc_encrypt_a32(file_mac, ul_key[:4])

            #encrypt file and upload
            chunk = aes.encrypt(chunk)
            output_file = requests.post(ul_url + "/" + str(chunk_start), data=chunk, timeout=self.timeout)
            completion_file_handle = output_file.text

        #determine meta mac
        meta_mac = (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3])

        attribs = {'n': os.path.basename(filename)}
        encrypt_attribs = base64_url_encode(encrypt_attr(attribs, ul_key[:4]))
        key = [ul_key[0] ^ ul_key[4], ul_key[1] ^ ul_key[5], ul_key[2] ^ meta_mac[0], ul_key[3] ^ meta_mac[1],
               ul_key[4], ul_key[5], meta_mac[0], meta_mac[1]]
        encrypted_key = a32_to_base64(encrypt_key(key, self.master_key))
        #update attributes
        data = self.api_request({'a': 'p', 't': dest, 'n': [
            {'h': completion_file_handle, 't': 0, 'a': encrypt_attribs, 'k': encrypted_key}]}
        )
        return data

    def process_file(self, file):
        if file['t'] == 0 or file['t'] == 1:
            key = file['k'][file['k'].index(':') + 1:]
            key = decrypt_key(base64_to_a32(key), self.master_key)
            if file['t'] == 0:
                k = file['k'] = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
                iv = file['iv'] = key[4:6] + (0, 0)
                meta_mac = file['meta_mac'] = key[6:8]
            else:
                k = file['k'] = key
            attributes = base64_url_decode(file['a'])
            attributes = decrypt_attr(attributes, k)
            file['a'] = attributes
        elif file['t'] == 2:
            self.root_id = file['h']
            file['a'] = {'n': 'Cloud Drive'}
        elif file['t'] == 3:
            self.inbox_id = file['h']
            file['a'] = {'n': 'Inbox'}
        elif file['t'] == 4:
            self.trashbin_id = file['h']
            file['a'] = {'n': 'Rubbish Bin'}
        return file