from imports import *
from config import *
from routes import *
from handlers import *
from models import *

redirect__uri = 'http://www.openflock.co/authorization'
client__id = 'ADD YOUR CLIENT_ID HERE'
client__secret = 'ADD YOUR CLIENT SECRET ID HERE'


class AuthRedirect(BaseHandler):
	def get(self):
			self.redirect('https://github.com/login/oauth/authorize?state=openflock&redirect_uri='+redirect__uri+'&client_id='+client__id)


class Authorization(BaseHandler):
	def get(self):
		headers = {
		'User-Agent': 'Openflock'
		}

		url_queries = self.request.GET
		state = url_queries['state']
		code = url_queries['code']
		url = 'https://github.com/login/oauth/access_token?client_id='+client__id+'&client_secret='+client__secret+'&redirect_uri='+redirect__uri+'&scope=&code='+str(code)
		req = requests.post(url,headers=headers)
		req = str(req.content)
		access_token = ""
		i=13
		while(req[i]!='&'):
			access_token = access_token + req[i]
			i = i + 1

		user_api_url = 'https://api.github.com/user?access_token='+str(access_token)
		user_json_data = requests.get(user_api_url,headers=headers)
		d = json.loads(user_json_data.content)
		username = d['login']

		self.response.out.write(str(access_token)+user_api_url)
		if d['name']:
			fullname = d['name']
		else:
			fullname = str(username)

		self.session['username'] = username
		avatar_url = d['avatar_url']
		user_html_url = d['html_url']

		if d['blog']:
			website = d['blog']
		else:
			website=""

		if d['email']:
			email = d['email']
		else:
			email=""

		if d['location']:
			location = d['location']
		else:
			location=""

		public_repos = d['public_repos']
		followers = d['followers']
		following = d['following']
		repos_url = d['repos_url']		

		repos_url = repos_url + "?access_token="+access_token
		lang = []
		res = requests.get(repos_url,headers=headers)
		response_code = res.status_code
		if(response_code != 200):
			self.response.out.write(str(response_code) + " " + str(res.headers) + " Something's wrong with GitHub API!")
			return
		elif response_code == 200:
			cont = res.json()
			for item in cont:
				if item['fork']==False and item['private']==False:
					reponame = item['name']
					repo_html_url = item['html_url']
					username = item['owner']['login']
					if item['language']:
						language = item['language']
						lang.append(language)
					else:
						language="none"
					forks = item['forks']
					stars = item['stargazers_count']
					homepage = item['homepage']
					description = item['description']

					repo_instance = RepoData(key_name=reponame,reponame=reponame,repo_html_url=repo_html_url,username=username,language=language,forks=str(forks),stars=str(stars),website=homepage,description=description)
					repo_instance.put()
		lang_list = list(set(lang))
		if None in lang_list:
			lang_list.remove(None)



		orgs_url = 'https://api.github.com/users/'+str(username)+'/orgs?access_token='+str(access_token)
		orgs=[]
		org_details = requests.get(orgs_url,headers=headers)
		response_code=org_details.status_code
		if response_code != 200:
			self.response.out.write(str(response_code)+" Something's wrong...Moslty with interaction of Openflock with GitHub API!")
		elif response_code == 200:
			result = org_details.json()
			for org in result:
				org_username = org['login']
				orgs.append(org_username)



		user_instance = UserData(key_name=username,fullname=fullname,username=username,orgs=orgs,access_token=str(access_token),email=email,location=location,website=website,lang_list=lang_list,public_repos=str(public_repos),followers=str(followers),following=str(following),avatar_url=avatar_url)
		user_instance.put()
		self.redirect('/')





