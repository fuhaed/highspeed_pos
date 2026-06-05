from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("HIGHSPEED POS"),
			"items": [
				 {
				   "description": "HIGHSPEED POS", 
				   "name": "hsposapp", 
				   "label": "POSAPP", 					
				   "type": "page"
				  }, 

				{
				   "type": "doctype", 
				   "description": "POS Profile", 
				   "name": "POS Profile", 
				  },

				{
				   "type": "doctype", 
				   "description": "HSPOS Opening Shift", 
				   "name": "HSPOS Opening Shift", 
				  },
				{
				   "type": "doctype", 
				   "description": "HSPOS Closing Shift", 
				   "name": "HSPOS Closing Shift", 
				  },
				{
				   "type": "doctype", 
				   "description": "HSPOS Offers", 
				   "name": "HSPOS Offer", 
				  },
            ]

        }
	]
