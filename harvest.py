import sys,optparse,argparse
import json, csv, urllib2
from unidecode import unidecode

parser = argparse.ArgumentParser(description='Creates email addresses with optional formatters from names of employees of a company on LinkedIn.')
parser.add_argument(
	"--company",
	metavar="company-id",
	help='Company Identificator'
)

parser.add_argument(
	"--cookie-file",
	help='Cookie file',
	default="cookie.txt",
	type=argparse.FileType('rb')
)

parser.add_argument(
	"--email-format",
	help="Email Format (eg: {first:1.1}{last}@domain.xyz, {first}.{last}@domain.com)"
)

args = parser.parse_args()

company_id = args.company
email_format = args.email_format

#get cookies
content = args.cookie_file.readlines()
csrf_token = content[0].strip()
session_id = content[1].strip()

cookie1 = 'li_at='+session_id
cookie2 = 'JSESSIONID='+csrf_token

last_page = False

def normalize(str, remove_specials = True, remove_accents = True, remove_certs = True):
	pass

employees = []

def harvest(curr):
	global last_page
	global employees

	url = ("https://www.linkedin.com/voyager/api/search/blended?"
	"count=49&origin=OTHER&queryContext=List(spellCorrectionEnabled-%3Etrue,"
	"crelatedSearchesEnabled-%3Etrue,kcardTypes-%3EPROFILE%7CCOMPANY)&q=all&filters=List(currentCompany-%3E" + company_id + ",resultType-%3EPEOPLE)&start=" + str(curr))
	opener = urllib2.build_opener()
	opener.addheaders.append(('csrf-token', csrf_token))
	opener.addheaders.append(('Cookie', cookie1 + ';' + cookie2))
	opener.addheaders.append(('x-restli-protocol-version', '2.0.0'))
	response = opener.open(url)

	data = json.load(response)
	data = data["elements"][0]
	data = data["elements"]

	if len(data) != 49:
		last_page = True

	for profile in data:
		employee = profile["image"]["attributes"][0]["miniProfile"]

		first = employee["firstName"]
		first = first.split(" ")[0] if " " in first else first

		last = employee["lastName"]
		last = last.split(",")[0] if "," in last else last
		last = last.split(" - ")[0] if " - " in last else last
		last = last.split(" ")[-1] if " " in last else last

		print "{};{};{}".format(
			employee["firstName"].encode("utf-8"),
			email_format.format(**{
				"first":  unidecode(first),
				"last": unidecode(last),
			}).lower(),
			employee["occupation"].encode("utf-8")
		)

curr = 0
while not last_page:
	harvest(curr)
	curr = curr + 49
      


