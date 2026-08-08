import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# Logic puzzle: determine who is guilty based on statements
# Key constraints:
# 1. At most 2 people are guilty (getaway car holds 2)
# 2. Innocent people tell the truth, guilty people lie
# 
# Statements:
# ARTIE: "It wasn't me." (Artie is innocent)
# BILL: "Crackitt was in it up to his neck." (Crackitt is guilty)
# CRACKITT: "No I wasn't." (Crackitt is innocent)
# DODGY: "If Crackitt did it, Bill did it with him." (Crackitt guilty implies Bill guilty)
# EDGY: "Nobody did it alone." (number of guilty != 1)
# FINGERS: "That's right: it was Artie and Dodgy together." (Artie and Dodgy both guilty, exactly 2 total)

# Step 2: Model with CPMpy
# Decision variables: 1 if guilty, 0 if innocent
artie = cp.boolvar(name="artie")
bill = cp.boolvar(name="bill") 
crackitt = cp.boolvar(name="crackitt")
dodgy = cp.boolvar(name="dodgy")
edgy = cp.boolvar(name="edgy")
fingers = cp.boolvar(name="fingers")

suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

model = cp.Model()

# Constraint: At most 2 people are guilty (getaway car constraint)
model += cp.sum(suspects) <= 2

# Truth/lie constraints: Each person tells truth if innocent, lies if guilty

# ARTIE: "It wasn't me" - statement is ~artie
artie_statement = ~artie
model += (~artie).implies(artie_statement)  # If innocent, statement is true
model += artie.implies(~artie_statement)    # If guilty, statement is false

# BILL: "Crackitt was in it up to his neck" - statement is crackitt
bill_statement = crackitt
model += (~bill).implies(bill_statement)   # If Bill innocent, Crackitt is guilty
model += bill.implies(~bill_statement)     # If Bill guilty, Crackitt is innocent

# CRACKITT: "No I wasn't" - statement is ~crackitt  
crackitt_statement = ~crackitt
model += (~crackitt).implies(crackitt_statement)   # If Crackitt innocent, statement true
model += crackitt.implies(~crackitt_statement)     # If Crackitt guilty, statement false

# DODGY: "If Crackitt did it, Bill did it with him" - statement is (crackitt implies bill)
dodgy_statement = crackitt.implies(bill)
model += (~dodgy).implies(dodgy_statement)     # If Dodgy innocent, implication holds
model += dodgy.implies(~dodgy_statement)       # If Dodgy guilty, implication is false

# EDGY: "Nobody did it alone" - statement is (sum(suspects) != 1)
edgy_statement = (cp.sum(suspects) != 1)
model += (~edgy).implies(edgy_statement)       # If Edgy innocent, not exactly 1 guilty
model += edgy.implies(~edgy_statement)         # If Edgy guilty, exactly 1 guilty

# FINGERS: "That's right: it was Artie and Dodgy together" 
# Statement is (artie AND dodgy AND exactly 2 guilty)
fingers_statement = artie & dodgy & (cp.sum(suspects) == 2)
model += (~fingers).implies(fingers_statement)  # If Fingers innocent, Artie+Dodgy did it
model += fingers.implies(~fingers_statement)    # If Fingers guilty, not Artie+Dodgy

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    solution = {
        "artie": int(artie.value()),
        "bill": int(bill.value()),
        "crackitt": int(crackitt.value()),
        "dodgy": int(dodgy.value()),
        "edgy": int(edgy.value()),
        "fingers": int(fingers.value())
    }
    
    # Verification
    def verify_solution(sol):
        a, b, c, d, e, f = sol["artie"], sol["bill"], sol["crackitt"], sol["dodgy"], sol["edgy"], sol["fingers"]
        
        # Check at most 2 guilty
        total_guilty = a + b + c + d + e + f
        if total_guilty > 2:
            return False
            
        # Check truth/lie consistency for each statement
        # Innocent people tell truth, guilty people lie
        
        # ARTIE: "It wasn't me" 
        if (a == 0) != ((a == 0) == True):  # innocent tells truth about being innocent
            return False
            
        # BILL: "Crackitt was in it"
        if (b == 0) != (c == 1):  # innocent Bill says truth about Crackitt
            return False
            
        # CRACKITT: "No I wasn't"
        if (c == 0) != (c == 0):  # innocent Crackitt tells truth about being innocent
            return False
            
        # DODGY: "If Crackitt did it, Bill did it with him"
        if (d == 0) != ((not c) or b):  # innocent Dodgy tells truth about implication
            return False
            
        # EDGY: "Nobody did it alone"
        if (e == 0) != (total_guilty != 1):  # innocent Edgy tells truth about not alone
            return False
            
        # FINGERS: "It was Artie and Dodgy together"
        if (f == 0) != (a == 1 and d == 1 and total_guilty == 2):  # innocent Fingers tells truth
            return False
            
        return True
    
    assert verify_solution(solution), "Solution verification failed!"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))