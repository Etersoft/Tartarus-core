
import Ice, IcePy

def create(cls, ad, cat, name):
    if isinstance(ad, IcePy.Current):
        ad = ad.adapter
    com = ad.getCommunicator()
    id = com.stringToIdentity("%s/%s" % (cat,name))
    pr = ad.createProxy(id)
    return cls.uncheckedCast(pr)

