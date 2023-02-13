from flask import Flask;
from flask_cors import CORS ,cross_origin
import pandas as pd;
import numpy as np;
import pymysql;
import mysql
import mysql.connector
from sqlalchemy.pool import QueuePool
from sqlalchemy import text
import sqlalchemy;
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

#------------------------------DB CONFIG------------------------


# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:root@localhost:3306/machine_learning"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)





#-----------------------DB CONFIG END-----------------------------


def recommend(userName,pt,similarity_score):
    filtered_similar_items=[];
    
    index = np.where(pt.index == userName)[0][0];
    similar_items = sorted(list(enumerate(similarity_score[index])),key=lambda x:x[1],reverse=True)[0:100];
    
    for i in similar_items:
        if(i[1] > 0.5):
            if(pt.index[i[0]] == userName):
                continue;
            else:
                filtered_similar_items.append(pt.index[i[0]]);
    return filtered_similar_items;


@app.route('/<userName>')
def recommendationSystem(userName):

    conn = mysql.connector.connect(
        host="database-1.cqseadaorxhc.ap-south-1.rds.amazonaws.com",
        user="afshal",
        password="afshal123.",
        database="machine_learning"
    )


    query = '''SELECT * from test'''


    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()



    data = pd.DataFrame(result,columns=['id', 'user', 'interest', 'category'])
    

    cur.close()
    conn.close()


    # Label Encoder

    category = LabelEncoder()
    data['category'] = category.fit_transform(data['category']) + 1

    
    # pivot table

    pt = data.pivot_table(index='user',columns='interest',values='category');

    
    # Fill NaN to 0

    pt.fillna(0,inplace=True)


    # Calculating Similarity Score with cosine similarity

    similarity_score = cosine_similarity(pt)


    # Calling Recommend function

    getUsers = recommend(userName,pt,similarity_score)

    return getUsers


@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', "*")
    return response

# App Main Start

if(__name__ == "__main__"):
    app.run(debug=True)