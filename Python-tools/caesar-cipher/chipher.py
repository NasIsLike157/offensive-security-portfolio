#!/usr/bin/env python3
import argparse

class Cipher:
    
    def __init__(self,shift):
        self.shift_value = shift

    def _char2code(self,char):
        return ord(char) - ord('A')

    def _code2char(self,code):
        return chr(code + ord('A'))
    

    def _encrypt_char(self, char):
        
        code = self._char2code(char)
        
        if code < 0 or code > 25:
            return char 
        
        encrypted_code = (code + self.shift_value) % 26

        return self._code2char(encrypted_code)

    
    def _decrypt_char(self,char):
        code = self._char2code(char)
        
        if code < 0 or code > 25:
            return char

        decrypted_code = (code - self.shift_value) % 26

        return self._code2char(decrypted_code)


    def encrypt(self,plain_text):
        chipher_text = []

        for i , c in enumerate(plain_text):
            chipher_text.append(self._encrypt_char(plain_text[i]))

        return "".join(chipher_text)


    def decrypt(self,chipher_text):
        plain_text = []

        for i , c in enumerate(chipher_text):
            plain_text.append(self._decrypt_char(chipher_text[i]))

        return "".join(plain_text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--shift",type=int)
    parser.add_argument("-e", "--encrypt",action="store_true")
    parser.add_argument("-d", "--decrypt",action="store_true")
    args = parser.parse_args()

    shift_value = args.shift or 3
    cipher = Cipher(shift=shift_value)
    user_input = input("Enter text to cipher: > ")
    plain_text = user_input.upper()

    if args.encrypt:
        chihpre_text = cipher.encrypt(plain_text)
    if args.decrypt:
        chihpre_text = cipher.decrypt(plain_text)
    else:
        print("Must Specify Encription (-e) or decription (-d)")
    
    
    print(f'{chihpre_text}')

if __name__ == '__main__':
    main()