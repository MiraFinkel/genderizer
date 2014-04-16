import memcache
import pickle


class MemcacheNamesCollection(object):
    mcclient = memcache.Client(['127.0.0.1:11211'], debug=0)
    isInitialized = None

    collectionSourceFile = 'name_gender.csv'
    collectionName = 'firstNames'
    collection = None

    @classmethod
    def init(cls):
        cls.collection = cls.cache_retrieve(cls.collectionName)
        if not cls.collection:
            items = cls.loadFromSource()
            cls.cache_store(cls.collectionName, items)

    @classmethod
    def cache_store(cls, key, value, chunksize=950000):
      serialized = pickle.dumps(value, 2)
      values = {}
      for i in xrange(0, len(serialized), chunksize):
        values['%s.%s' % (key, i//chunksize)] = serialized[i : i+chunksize]
      cls.mcclient.set_multi(values)
    
    @classmethod
    def cache_retrieve(cls, key):
        result = cls.mcclient.get_multi(['%s.%s' % (key, i) for i in xrange(32)])
        serialized = ''.join([v for v in result.values() if v is not None])
        if serialized:
            return pickle.loads(serialized)
        else:
            return None

    @classmethod
    def loadFromSource(cls):
        # will produce something like this: 
        # {'kamil': {'tr': 'm'}, 'mustafa': {'en': 'm', 'tr': 'm'}, 'kim': {'sk': 'm', 'nl': 'f'}}
        items = {}
        for i in open(cls.collectionSourceFile):
            
            item = i.strip().split(',')
            firstName = item[0].lower()
            
            if len(item) == 2:
                item.append('en')

            item = {item[2]:item[1]}

            if firstName in items:
                items[firstName] = dict(items[firstName].items() + item.items())
            else:
                items[firstName] = item

        return items


    @classmethod
    def getGender(cls, firstName, lang='en'):
        if not cls.isInitialized:
            cls.init()

        firstName = firstName.lower()
        nameInfo = cls.collection.get(firstName, None)
        if not nameInfo:
            return None

        if nameInfo.get(lang, None):
            return {'name': firstName, 'gender': nameInfo[lang], 'lang': lang}
        elif nameInfo.get('en', None):
            return {'name': firstName, 'gender': nameInfo['en'], 'lang': 'en'}
        else:
            return None
        

#print MemcacheNamesCollection.getGender(firstName='mustafa', lang='fr')

