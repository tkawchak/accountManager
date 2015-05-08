# functions for encrypting and decrypting text in files

# in order to use decryption, the shift should
# be the opposite of that used for encryption and
# the characters list should be the same as
# the original

import string


def encrypt(sequence, characters, shift, reservedSymbols = string.punctuation):
    """function to encrypt a set of characters
        @param sequence (string) - the sequence to be encrypted
        @param characters (string) - the characters involved in the encryption
            @invariant - no duplicate characters
        @param shift (int) - the magnitude of the shift
        @param reservedSymbols (string) - characters that should not be changed when encrypting
        @return (string) - the encrypted string
    """

    newSequenceArray=[]  # gets populated with the new characters after being shifted
    
    # POPULATE NEW SEQUENCY WITH THE SHIFTED CHARACTERS
    for i in sequence:

        if i in reservedSymbols or i not in characters:
            newSequenceArray.append(i)
            print('character \'%s\' not encrypted because it is a reserved symbol' % i)

        else:
            # FIND THE INDEX OF THE CHARACTER FROM THE SEQUENCE IN THE LIST OF CHARACTERS
            charIndex = characters.index(i)

            # APPLIES THE SHIFT TO FIND THE NEW CHARACTER
            newCharIndex = charIndex + shift
            # CHECKS TO MAKE SURE THE NEW INDEX IS WITHIN THE STRING BOUNDS
            # CAN THIS BE DONE WITH THE MODULO OPERATOR?????
            while newCharIndex >= len(characters):
                newCharIndex = newCharIndex - len(characters)
            while newCharIndex < 0:
                newCharIndex = newCharIndex + len(characters)

            # ADDS THE NEW CHARACTER TO THE ARRAY OF NEW CHARACTERS
            newSequenceArray.append(characters[newCharIndex])
            
    # CREATES ARRAY OF NEW CHARACTERS
    newSequence = ''.join(newSequenceArray)

    # CHECKS TO SEE IF THE NEW PASSWORD IS THE SAME LENGTH AS THE ORIGINAL SEQUENCE.  SIMPLE ERROR CHECK
    if newSequence != sequence and len(newSequence) == len(sequence) or newSequence == '':
        return newSequence
    # ELSE THERE WAS AN ERROR IN ENCRYPTION
    else:
        print('\'%s\' has not been encrypted. Please edit!' % sequence)
        return sequence
