from flask import Flask, render_template,request,redirect,url_for
import xlsxwriter
from xlsxwriter import Workbook
import csv
import os
import csv 
import matplotlib
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt 
from database import OracleDB
from werkzeug.utils import secure_filename
from flask_ngrok import run_with_ngrok
from pyngrok import ngrok

ngrok_auth="2P1GO3k0AAJ1voddYl1KKgcRD2F_7DiGn5a8o1fr2nWSqjh7F"

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# run_with_ngrok(app)
# ngrok.set_auth_token(ngrok_auth)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["STATIC_IMAGE"] ="static/images"

@app.route("/")
@app.route("/home")
def hello():
    return render_template("home.html", title="Home page")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404


@app.route("/amazonLaptop", methods=["GET","POST"])
def amazonLaptop():
    if request.method == "POST":
        file=request.files["datafile"]
        if file:
            filename = secure_filename(file.filename)
            #print("filename:", filename)
            file_path=os.path.join(app.config["UPLOAD_FOLDER"],filename)
            #print("file_path:",file_path)
            file.save(file_path)
            
            data=[]
            with open(file_path, encoding='latin1') as file_object:
                reader_object = csv.reader(file_object)
                
                # skip the first row
                next(reader_object)
                
                for row in reader_object:
                    #print(row)
                    data.append(row)

                if data:
                    with OracleDB().get_connection() as connection:
                        insert_statement='''
                                        insert into amazon_laptop(
                                        PRODUCT_ID,
                                        PRODUCT_DESCRIPTION,
                                        RATING_SCORE,
                                        NUMBER_OF_GLOBAL_RATING,
                                        CURRENT_PRICE,
                                        ORIGINAL_PRICE,
                                        OPERATING_SYSTEM,
                                        BRAND,
                                        HAVING_DISCOUNT,
                                        DISPLAY_SIZE_INCHES,
                                        DISK_SIZE_GB,
                                        RAM_GB
                                        )values(
                                        :PRODUCT_ID,
                                        :PRODUCT_DESCRIPTION,
                                        :RATING_SCORE,
                                        :NUMBER_OF_GLOBAL_RATING,
                                        :CURRENT_PRICE,
                                        :ORIGINAL_PRICE,
                                        :OPERATING_SYSTEM,
                                        :BRAND,
                                        :HAVING_DISCOUNT,
                                        :DISPLAY_SIZE_INCHES,
                                        :DISK_SIZE_GB,
                                        :RAM_GB
                                        )
                                        '''
                        cursor = connection.cursor()
                        cursor.executemany(insert_statement, data)
                        connection.commit()
                return redirect(url_for("amazonLaptop"))

    elif request.method=="GET":
        with OracleDB().get_connection()as connection:
            query = '''
                    select * from amazon_laptop
                    '''
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            #print(len(data))
            
        
        return render_template("amazonLaptop.html", title="Amazon Laptop", data=data)
    

#export
@app.route("/export",methods=["GET"])
def export():
    # # to csv
    # with OracleDB().get_connection() as connection:
    #     cursor = connection.cursor()
    #     csv_file = open("amazon_laptop_edit.csv", "w")
    #     writer = csv.writer(csv_file, delimiter='|', lineterminator="\n", quoting=csv.QUOTE_NONE,escapechar='\\')
    #     r = cursor.execute("SELECT * FROM amazon_laptop")
    #     for row in cursor:
    #         writer.writerow(row)

    #     cursor.close()
    #     csv_file.close()

    # # to excel
    with OracleDB().get_connection() as connection:
        cursor = connection.cursor()
        workbook = xlsxwriter.Workbook(r'C:\Users\yq89_\Downloads\amazon_laptop_edit.xlsx')
        sheet = workbook.add_worksheet()

        cursor.execute("select * from amazon_laptop")
        for r, row in enumerate(cursor.fetchall()):
                for c, col in enumerate(row):
                        sheet.write(r, c, col)

        workbook.close()
        cursor.close()
        return redirect(url_for('amazonLaptop'))

#dashboard

@app.route("/dashboard", methods=["GET"])
def dashboard():
    with OracleDB().get_connection() as connection:
        query = '''
            SELECT brand, nvl(AVG(rating_score),0) AS avg_rating, nvl(SUM(number_of_global_rating),0) AS total_orders
            FROM amazon_laptop
            GROUP BY brand
            ORDER BY nvl(AVG(rating_score),0) DESC
            '''
        cursor = connection.cursor()
        cursor.execute(query)
        rows = []
        avg_ratings = []
        total_orders = []
        for row in cursor:
            rows.append(row[0])
            avg_ratings.append(row[1])
            total_orders.append(row[2])
        fig, ax = plt.subplots(ncols=2, figsize=(20, 10))
        ax[0].bar(rows, avg_ratings, color=['#008080', '#20B2AA', '#3CB371', '#00FF7F', '#ADFF2F', '#FFFF00', '#FFD700', '#FFA500', '#FF8C00', '#FF6347'])
        ax[0].set_title('Average Rating Score by Brand')
        ax[0].set_xlabel('Brand')
        ax[0].set_ylabel('Average Rating Score')
        ax[1].bar(rows, total_orders, color=['#008080', '#20B2AA', '#3CB371', '#00FF7F', '#ADFF2F', '#FFFF00', '#FFD700', '#FFA500', '#FF8C00', '#FF6347'])
        ax[1].set_title('Number of Orders by Brand')
        ax[1].set_xlabel('Brand')
        ax[1].set_ylabel('Number of Orders')
        plt.tight_layout()
        my_file = "brand_stats.png"
        my_path = app.config["STATIC_IMAGE"]
        plt.savefig(os.path.join(my_path, my_file))
    return render_template("dashboard.html", title="Dashboard")



#edit
@app.route("/amazonLaptop_edit/<id>", methods=["GET","POST"])
def amazonLaptop_edit(id):
    print("amazonLaptop id:", id)
    data=None
    if request.method == "GET":
        with OracleDB().get_connection() as connection:
            query='''
                    select * from amazon_laptop where product_id = :product_id
                ''' 
            cursor = connection.cursor()
            cursor.execute(query,PRODUCT_ID = id)
            data = cursor.fetchone()
            return render_template("amazonLaptop_edit.html",title="Edit Information", data=data)
    elif request.method == "POST":
        PRODUCT_DESCRIPTION = request.form.get("PRODUCT_DESCRIPTION")
        RATING_SCORE = request.form.get("RATING_SCORE")
        NUMBER_OF_GLOBAL_RATING = request.form.get("NUMBER_OF_GLOBAL_RATING")
        CURRENT_PRICE = request.form.get("CURRENT_PRICE")
        ORIGINAL_PRICE = request.form.get("ORIGINAL_PRICE")
        OPERATING_SYSTEM = request.form.get("OPERATING_SYSTEM")
        BRAND = request.form.get("BRAND")
        HAVING_DISCOUNT = request.form.get("HAVING_DISCOUNT")
        DISPLAY_SIZE_INCHES = request.form.get("DISPLAY_SIZE_INCHES")
        DISK_SIZE_GB = request.form.get("DISK_SIZE_GB")
        RAM_GB = request.form.get("RAM_GB")
        
        with OracleDB().get_connection() as connection:
            query='''
                    update amazon_laptop
                    set 
                    PRODUCT_DESCRIPTION=:PRODUCT_DESCRIPTION,
                    RATING_SCORE=:RATING_SCORE,
                    NUMBER_OF_GLOBAL_RATING=:NUMBER_OF_GLOBAL_RATING,
                    CURRENT_PRICE=:CURRENT_PRICE,
                    ORIGINAL_PRICE=:ORIGINAL_PRICE,
                    OPERATING_SYSTEM=:OPERATING_SYSTEM,
                    BRAND=:BRAND,
                    HAVING_DISCOUNT=:HAVING_DISCOUNT,
                    DISPLAY_SIZE_INCHES=:DISPLAY_SIZE_INCHES,
                    DISK_SIZE_GB=:DISK_SIZE_GB,
                    RAM_GB=:RAM_GB
                    where PRODUCT_ID = :PRODUCT_ID
                ''' 
            cursor = connection.cursor()
            cursor.execute(query,PRODUCT_ID = id, 
                            PRODUCT_DESCRIPTION=PRODUCT_DESCRIPTION,
                            RATING_SCORE=RATING_SCORE,
                            NUMBER_OF_GLOBAL_RATING=NUMBER_OF_GLOBAL_RATING,
                            CURRENT_PRICE=CURRENT_PRICE,
                            ORIGINAL_PRICE=ORIGINAL_PRICE,
                            OPERATING_SYSTEM=OPERATING_SYSTEM,
                            BRAND=BRAND,
                            HAVING_DISCOUNT=HAVING_DISCOUNT,
                            DISPLAY_SIZE_INCHES=DISPLAY_SIZE_INCHES,
                            DISK_SIZE_GB=DISK_SIZE_GB,
                            RAM_GB=RAM_GB)
            connection.commit()
            return redirect( url_for("amazonLaptop"))

#delete
@app.route("/amazonLaptop_delete/<id>", methods=["GET","POST"])
def amazonLaptop_delete(id):
    #print("amazonLaptop id:", id)
    data=None
    if request.method == "GET":
        with OracleDB().get_connection() as connection:
            query='''
                    select * from amazon_laptop 
                    where PRODUCT_ID = :PRODUCT_ID
                ''' 
            cursor = connection.cursor()
            cursor.execute(query,PRODUCT_ID = id)
            data = cursor.fetchone()
            return render_template("amazonLaptop_delete.html",title="Delete Information", data=data)
    elif request.method == "POST":        
        with OracleDB().get_connection() as connection:
            query='''
                    delete from amazon_laptop 
                    where PRODUCT_ID = :PRODUCT_ID
                ''' 
            cursor = connection.cursor()
            cursor.execute(query, PRODUCT_ID = id)
            connection.commit()
            return redirect( url_for("amazonLaptop"))

#add
@app.route("/amazonLaptop_add", methods=["GET","POST"])
def amazonLaptop_add():
    data=None
    if request.method == "GET":
        return render_template("amazonLaptop_add.html", title= "Add Information")
    elif request.method == "POST":
        with OracleDB().get_connection() as connection:
            cursor = connection.cursor()
            
            insert_statement ='''
                         insert into amazon_laptop(
                                        PRODUCT_ID,
                                        PRODUCT_DESCRIPTION,
                                        RATING_SCORE,
                                        NUMBER_OF_GLOBAL_RATING,
                                        CURRENT_PRICE,
                                        ORIGINAL_PRICE,
                                        OPERATING_SYSTEM,
                                        BRAND,
                                        HAVING_DISCOUNT,
                                        DISPLAY_SIZE_INCHES,
                                        DISK_SIZE_GB,
                                        RAM_GB
                                        )values(
                                        :PRODUCT_ID,
                                        :PRODUCT_DESCRIPTION,
                                        :RATING_SCORE,
                                        :NUMBER_OF_GLOBAL_RATING,
                                        :CURRENT_PRICE,
                                        :ORIGINAL_PRICE,
                                        :OPERATING_SYSTEM,
                                        :BRAND,
                                        :HAVING_DISCOUNT,
                                        :DISPLAY_SIZE_INCHES,
                                        :DISK_SIZE_GB,
                                        :RAM_GB
                                        )
                            ''' 
            seq_statement = '''
                            select amazon_laptop_seq.nextval from dual
                            '''
            cursor.execute(seq_statement)
            
            PRODUCT_ID = cursor.fetchone()[0]
            PRODUCT_DESCRIPTION = request.form.get("PRODUCT_DESCRIPTION")
            RATING_SCORE = request.form.get("RATING_SCORE")
            NUMBER_OF_GLOBAL_RATING = request.form.get("NUMBER_OF_GLOBAL_RATING")
            CURRENT_PRICE = request.form.get("CURRENT_PRICE")
            ORIGINAL_PRICE = request.form.get("ORIGINAL_PRICE")
            OPERATING_SYSTEM = request.form.get("OPERATING_SYSTEM")
            BRAND = request.form.get("BRAND")
            HAVING_DISCOUNT = request.form.get("HAVING_DISCOUNT")
            DISPLAY_SIZE_INCHES = request.form.get("DISPLAY_SIZE_INCHES")
            DISK_SIZE_GB = request.form.get("DISK_SIZE_GB")
            RAM_GB = request.form.get("RAM_GB")
            
            cursor.execute(insert_statement, 
                        PRODUCT_ID=PRODUCT_ID,
                        PRODUCT_DESCRIPTION=PRODUCT_DESCRIPTION,
                        RATING_SCORE=RATING_SCORE,
                        NUMBER_OF_GLOBAL_RATING=NUMBER_OF_GLOBAL_RATING,
                        CURRENT_PRICE=CURRENT_PRICE,
                        ORIGINAL_PRICE=ORIGINAL_PRICE,
                        OPERATING_SYSTEM=OPERATING_SYSTEM,
                        BRAND=BRAND,
                        HAVING_DISCOUNT=HAVING_DISCOUNT,
                        DISPLAY_SIZE_INCHES=DISPLAY_SIZE_INCHES,
                        DISK_SIZE_GB=DISK_SIZE_GB,
                        RAM_GB=RAM_GB)
            connection.commit()
            return redirect( url_for("amazonLaptop"))
    return render_template("amazonLaptop_add.html",title="Add Information", data=data)


if __name__ == "__main__":
    #print("do something")
    app.run()