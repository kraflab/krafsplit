# key input hash  
wasHit = {}

# set key to the "hit" state
def hitKey(key):
    wasHit[key] = True

# was this key hit?
def hit(key):
    if key in wasHit:
        del(wasHit[key])
        return True
    else:
        return False
