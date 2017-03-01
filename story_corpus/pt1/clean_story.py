from bs4 import BeautifulSoup as BS
import re
def clean_story(file_name):

	print('Processing story ' + file_name)
	# extract the basic data out of html flags
	with open(file_name) as f:
		soup = BS(''.join(f.readlines()), 'html.parser')

	title = ''
	story = ''

	number_of_skips = 1

	for par in soup.find_all('p'):
		if number_of_skips > 0:
			number_of_skips -= 1
		elif not len(par.attrs) and not isinstance(par.contents[0], type(par)):
			story += par.text
		elif par.text.startswith('['):
			break

	# remove [1] etc for references
	story = re.sub('\[\d+]', '', story)

	return title, story
