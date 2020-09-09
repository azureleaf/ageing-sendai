from pydams import DAMS
from pydams.helpers import pretty_print

DAMS.init_dams()
address = u"千代田区"

# geocode() method
geocoded = DAMS.geocode(address)
pretty_print(geocoded)

# geocode_simplify() method
geocoded = DAMS.geocode_simplify(address)
pretty_print(geocoded)