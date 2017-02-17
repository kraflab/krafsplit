# key input hash  
wasHit = {}
def hitKey(key):
  wasHit[key] = True

def hit(key):
  if key in wasHit:
    del(wasHit[key])
    return True
  else:
    return False
