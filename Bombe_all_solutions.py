#This is bombe simulator which gives all possibly correct rotor configuration

#Gives all required libraries
import Enigma as e
from itertools import permutations
from multiprocessing import Pool
 
#Alphabet used
l1 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

#Given cipher and crib word (entered manually)
cipher = "EQHSZWYELRESOHNKGUVFVMFXWYTPGVVIWSFHFPVSJGIP"
crib = "THEBOUNTYISH"

#Parameters of crib word.
crib_length = len(crib)
first_crib_letter = crib[0]

#List for future cipher candidates.
crib_correspondences = []

#Loop that gives list of all possible cipher candidates for specific crib and cipher
for a in range(len(cipher) - crib_length + 1):
    for b in range(crib_length):
        if cipher[a + b] == crib[b]:
            break
            
        elif len(crib) - 1 == b:
            crib_correspondences.append(cipher[a:a + crib_length])

#Main loop which checks all possible option for a specific order of rotors.
def check_order(orders):

    #List of all possible solutions.
    total_solutions = []

    #Rotor order checked.
    rotor_order = list(orders)

    #Enigma is called as a dummy variable.
    machine = e.enigma(rotor_order, ["A","A","A"], ["A","A","A"])

    #Notches for middle and right rotors are saved.
    middle_notch = machine.rotorBuffer[1].notchPosition
    right_notch = machine.rotorBuffer[2].notchPosition

    #Loop checks each cipher candidate from list of possible crib positions.
    for cipher_candidate in crib_correspondences:
        crib_index = cipher.find(cipher_candidate)
        p = 0

        #Chooses all equivalence classes for offsets.
        for a  in range(26**3):
            if a / 26**3 > p+0.01:
                p = a / 26**3
                print(crib_index, p*100)

            #Chooses offsets itself.
            offset_right = a % 26
            offset_middle = (a // 26) % 26
            offset_left = a // 676

            #Chooses 3 options for middle notch.
            for b in range(3):

                #Chooses all options for right notch.
                for c in range(crib_length + 1):

                    if b==2 and c >= (crib_length - 1):
                        continue

                    #Sets rings and windows by offset and notches formulas.
                    right_position = (right_notch - c) % 26
                    middle_position = (middle_notch + [1, 0, -1][b]) % 26
                    
                    right_ring = (right_position - offset_right) % 26
                    middle_ring = (middle_position - offset_middle) % 26

                    window = [offset_left, middle_position, right_position]
                    rings = [0, middle_ring, right_ring]


                    #These two lists are made for logical propagations.
                    plugboard_variants = []

                    plugboard_solution = []


                    #This starts logical propagation for plugboard search.
                    for first_plug in l1:
                        decryption_test = "A"

                        #This is dictionary for plug connections that spread like in a graph tree.
                        #They are saved by assuptions and propagations.
                        plugboard_pairs = {}

                        #For assumption that letter is connected.
                        if first_crib_letter != first_plug:
                            plug_number = 1
                            plugboard_pairs[first_crib_letter] = first_plug
                            plugboard_pairs[first_plug] = first_crib_letter

                        #Not connected
                        else:
                            plug_number = 0
                            plugboard_pairs[first_crib_letter] = first_plug

                        #Appends needed assumption.
                        plugboard_variants.append((plugboard_pairs, plug_number))
                     
                        # Continues until all assumptions are destroyed.
                        while len(plugboard_variants) > 0:

                            #Removes assumption to test it by propagation or rejection.
                            plugboard_pairs, plug_number = plugboard_variants.pop()

                            #Indexes for contradiction and added consequences.
                            impossible = 0
                            added = 1

                            #Continues until no contradiction, consequences continue and plugs are fines.
                            while impossible == 0 and added == 1 and plug_number < 7:


                                added = 0

                                machine.rotorBuffer[0].rotorPosition = window[0]
                                machine.rotorBuffer[1].rotorPosition = window[1]
                                machine.rotorBuffer[2].rotorPosition = window[2]
                                machine.rotorBuffer[0].ringPosition = rings[0]
                                machine.rotorBuffer[1].ringPosition = rings[1]
                                machine.rotorBuffer[2].ringPosition = rings[2]

                                for d in range(crib_length):

                                    crib_letter = crib[d]
                                    cipher_letter = cipher_candidate[d]

                                    cribInBranch = (crib_letter in plugboard_pairs)

                                    #This is long check for logical contradictions.
                                    if cribInBranch or (cipher_letter in plugboard_pairs):

                                        if cribInBranch:

                                            plug_connection = plugboard_pairs[crib_letter]
                                            opposite_letter = cipher_letter

                                        else:
                                            plug_connection = plugboard_pairs[cipher_letter]
                                            opposite_letter = crib_letter

                                        rotor_output = machine.op(plug_connection)

                                        outputInBranch = (rotor_output not in plugboard_pairs)
                                        oppositeInBranch =  (opposite_letter not in plugboard_pairs)

                                        if outputInBranch and oppositeInBranch:

                                            plugboard_pairs[rotor_output] = opposite_letter
                                            plugboard_pairs[opposite_letter] = rotor_output

                                            added = 1

                                            if rotor_output != opposite_letter:

                                                plug_number += 1

                                        elif outputInBranch:

                                            if plugboard_pairs[opposite_letter] != rotor_output:

                                                impossible = 1

                                        elif oppositeInBranch:

                                            if plugboard_pairs[rotor_output] != opposite_letter:

                                                impossible = 1

                                        elif (plugboard_pairs[opposite_letter] != rotor_output) or (plugboard_pairs[rotor_output] != opposite_letter):

                                            impossible = 1
                                    #One rotor operation above does one step for enigma.
                                    else:
                                        machine.rotate(1)

                                    #Checks if contradiction was obtained.
                                    if impossible == 1 or plug_number > 6:
                                        break

                            #Checks if contradiction was obtained.
                            if impossible == 1 or plug_number > 6:
                                continue

                            #Checks if 6 plugs obtained work.
                            if plug_number == 6:

                                machine.rotorBuffer[0].rotorPosition = window[0]
                                machine.rotorBuffer[1].rotorPosition = window[1]
                                machine.rotorBuffer[2].rotorPosition = window[2]
                                machine.rotorBuffer[0].ringPosition = rings[0]
                                machine.rotorBuffer[1].ringPosition = rings[1]
                                machine.rotorBuffer[2].ringPosition = rings[2]

                                for plugboard_pair in plugboard_pairs:

                                    plug_connection = plugboard_pairs[plugboard_pair]

                                    if plugboard_pair < plug_connection:

                                        machine.plugboard.add(plugboard_pair, plug_connection)

                                        plugboard_solution.append(plugboard_pair+plugboard_pairs[plugboard_pair])
        
                                decryption_test = machine.op(cipher_candidate)

                                machine.plugboard.removeAll()

                                if crib == decryption_test:
                                    break

                                plugboard_solution = []

                                continue
    
                            letter_assumed = "NO"

                            #Checks if assumption was already made.
                            for assumption in l1:

                                if assumption not in plugboard_pairs:

                                    letter_assumed = assumption

                                    break

                            if letter_assumed == "NO":
                                continue

                            #Creates new assumption reviewing old assumptions.
                            for assumption in l1:
        
                                if assumption in plugboard_pairs:
                                    continue
        
                                plugboard_pairs_expanded = plugboard_pairs.copy()

                                if letter_assumed != assumption:

                                    plugboard_pairs_expanded[letter_assumed] = assumption
                                    plugboard_pairs_expanded[assumption] = letter_assumed

                                    plugboard_variants.append((plugboard_pairs_expanded, plug_number + 1))

                                else:
                                    plugboard_pairs_expanded[letter_assumed] = letter_assumed

                                    plugboard_variants.append((plugboard_pairs_expanded, plug_number))

                        #Checks if solution was obtained.
                        if crib == decryption_test:
                                break
                        
                    
                    #Checks if at least one solution was obtained.
                    if len(plugboard_solution) != 0: 

                        index = cipher.find(cipher_candidate)
     
                        if index == 0:

                            total_solutions.append((rotor_order, rings, window, plugboard_solution, crib_index))

                        #Makes backward steps of enigma if cipher candidate is not at position 0.
                        else:

                            while index != 0:
                    
                                if (middle_position != (middle_notch + 1) % 26 and middle_position != middle_notch) and right_position != (right_notch + 1) % 26:

                                    right_position = (right_position - 1) % 26

                                elif middle_position == (middle_notch + 1) % 26 and right_position != (right_notch + 1) % 26:

                                    right_position = (right_position - 1) % 26

                                elif middle_position != (middle_notch + 1) % 26 and middle_position != middle_notch and right_position == (right_notch + 1) % 26:

                                    middle_position = (middle_position - 1) % 26

                                    right_position = right_notch

                                elif middle_position == middle_notch:

                                    rings[2] = (right_notch + 1 + rings[2] - right_position) % 26

                                    right_position = right_notch

                                    middle_position = (middle_notch - 1) % 26

                                elif right_position == (right_notch + 1) % 26 and middle_position == (middle_notch + 1) % 26:

                                    right_position = (right_position - 1) % 26

                                    middle_position = (middle_position - 1) % 26

                                    offset_left = (offset_left - 1) % 26

                                index -= 1

                            window = [offset_left, middle_position, right_position]

                            total_solutions.append((rotor_order, rings, window, plugboard_solution, crib_index))

    return total_solutions


#This is multiprocessing for 6 rotor orders and output.
if __name__ == "__main__":

    pool = Pool(processes=6)

    fileName = "fileOutput"+crib+".txt"
    with open(fileName, "w", encoding="utf-8") as f:

        for test in pool.imap_unordered(check_order, permutations([1, 2, 3])):

            if len(test) > 0:

                for rotor_order, rings, window, plugboard_solution, crib_index in test:

                    machine = e.enigma(rotor_order, ["A","A","A"], ["A","A","A"])

                    machine.rotorBuffer[0].rotorPosition = window[0]
                    machine.rotorBuffer[1].rotorPosition = window[1]
                    machine.rotorBuffer[2].rotorPosition = window[2]
                    machine.rotorBuffer[0].ringPosition = rings[0]
                    machine.rotorBuffer[1].ringPosition = rings[1]
                    machine.rotorBuffer[2].ringPosition = rings[2]

                    for plugs in plugboard_solution:
                        machine.plugboard.add(plugs[0], plugs[1])

                    l2 = [machine.op(cipher), rotor_order, rings, window, plugboard_solution, crib_index]
                    
                    
                    print(l2, file=f)
    
    pool.close()
    pool.join()
