from flask import Flask,render_template,request
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
#import pymongo
#initialising application in flask
app  = Flask(__name__)
CORS(app)

#creating a seperate homepage for our live site
@app.route('/', methods = ['GET'])
#this helps for https request to prevent you from being blocked
@cross_origin()
def homePage():
    return render_template('index.html')

@app.route('/scrap',methods =['POST'])
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(' ','')
        try:
            # preparing the URL to search the product on flipkart
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString 
            # requesting the webpage from the internet
            uClient = uReq(flipkart_url)
            # reading the webpage
            flipkartPage = uClient.read()
            # closing the connection to the web server
            uClient.close() 
            # parsing the webpage as HTML
            flipkart_html = bs(flipkartPage, "html.parser")
            # seacrhing for appropriate tag to redirect to the product link
            bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"}) 
            # the first 3 members of the list do not contain relevant information, hence deleting them.
            del bigboxes[0:3] 
            #  taking the first iteration (for demo)
            box = bigboxes[0] 
            # extracting the actual product link
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] 
            # getting the product page from server
            prodRes = requests.get(productLink)
            # parsing the product page as HTML
            prod_html = bs(prodRes.text, "html.parser") 
            # finding the HTML section containing the customer comments
            commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"}) 

            #table = db[searchString] # creating a collection with the same name as search string. Tables and Collections are analogous.
            reviews = [] # initializing an empty list for reviews
            #  iterating over the comment section to get the details of customer and their comments
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except:
                    custComment = 'No Customer Comment'
                #fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")
                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                        "Comment": custComment} # saving that detail to a dictionary
                #table.insert_one(mydict) #insertig the dictionary containing the rview comments to the collection
                reviews.append(mydict) #  appending the comments to the review list
            return render_template('results.html', reviews=reviews) # showing the review to the user
        except:
            return 'something is wrong'
             


    else:
        return render_template('index.html')
        




if __name__ == "__main__":
    app.run(port=8000,debug =True)