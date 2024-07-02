from flask import Blueprint, render_template,request,url_for,redirect,session
from db_utils import get_db_connection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import base64
import os
import uuid
import json




db_connection = get_db_connection()
cursor = db_connection.cursor()

svm_bp = Blueprint("svm", __name__, template_folder="templates")
#prepare data for SVM models
data_sets = [
("U13-11-372984", "license_number"),
("Y05-04-823714", "license_number"),
("E25-09-678132", "license_number"),
("I21-06-319827", "license_number"),
("C30-12-582731", "license_number"),
("W09-08-419827", "license_number"),
("V14-03-812739", "license_number"),
("G28-10-927314", "license_number"),
("O19-07-543217", "license_number"),
("Z13-05-798213", "license_number"),
("A02-09-217834", "license_number"),
("B17-01-982374", "license_number"),
("K29-11-723489", "license_number"),
("R15-08-371928", "license_number"),
("D04-06-823714", "license_number"),
("P20-04-912873", "license_number"),
("H10-02-327984", "license_number"),
("L23-12-982374", "license_number"),
("Q14-12-528394", "license_number"),
    ("G20-05-817439", "license_number"),
    ("B11-03-638472", "license_number"),
    ("R16-09-297485", "license_number"),
    ("F27-01-782364", "license_number"),
    ("T08-10-193847", "license_number"),
    ("S14-04-826394", "license_number"),
    ("W22-01-947263", "license_number"),
    ("J03-04-672489", "license_number"),
    ("F08-06-189274", "license_number"),
    ("M19-11-827364", "license_number"),
    ("A01-01-123456", "license_number"),
    ("B02-02-234567", "license_number"),
    ("C03-03-345678", "license_number"),
    ("D39-23-001548", "license_number"),
    ("ELIJAH SANTOS", "name"),
("SOPHIA CRUZ", "name"),
("LUCAS RIVERA", "name"),
("LUNA DELA CRUZ", "name"),
("LIAM GONZALES", "name"),
("AMARA REYES", "name"),
("NOAH GARCIA", "name"),
("CHLOE DELA ROSA", "name"),
("ETHAN AQUINO", "name"),
("AVA MAGSAYSAY", "name"),
("MASON MACAPAGAL", "name"),
("HARPER BONIFACIO", "name"),
("JAMESON SANTOS", "name"),
("ZOE MAGALANG", "name"),
("EZRA MERCADO", "name"),
("ELLA CRUZ", "name"),
("LOGAN DELA ROSA", "name"),
("ARIA DELA CRUZ", "name"),
("CARTER REYES", "name"),
("LAYLA SANTIAGO", "name"),
("ALEXANDER CRUZ", "name"),
("SCARLETT SANTOS", "name"),
("OLIVER REYES", "name"),
("MADISON AQUINO", "name"),
("SEBASTIAN GARCIA", "name"),
("AVERY SANTOS", "name"),
("LIAM SANTIAGO", "name"),
("CHARLOTTE CRUZ", "name"),
("DANIEL REYES", "name"),
("MIA DELA ROSA", "name"),
("BENJAMIN AQUINO", "name"),
("LILY CRUZ", "name"),
("SAMUEL MAGALANG", "name"),
("EVELYN GARCIA", "name"),
("HENRY SANTOS", "name"),
("LUNA REYES", "name"),
("EMMA DELA CRUZ", "name"),
("JACK SANTIAGO", "name"),
("SOPHIA CRUZ", "name"),
("JACOB REYES", "name"),
("GRACE SANTOS", "name"),
("MICHAEL AQUINO", "name"),
("NORA MAGSAYSAY", "name"),
("WILLIAM MACAPAGAL", "name"),
("OLIVER REYES", "name"),
     ("2024/12/31", "expiration_date"),
    ("2025/01/01", "expiration_date"),
    ("2023/11/30", "expiration_date"),
    ("2024/10/15", "expiration_date"),
    ("2023/12/25", "expiration_date"),
    ("2025/05/20", "expiration_date"),
    ("2024/08/10", "expiration_date"),
    ("2023/09/05", "expiration_date"),
    ("2028/07/29", "expiration_date"),
    ("2025/02/28", "expiration_date"),
    ("2024/07/15", "expiration_date"),
    ("2023/10/31", "expiration_date"),
    ("2025/03/21", "expiration_date"),
    ("2024/09/30", "expiration_date"),
    ("2023/06/12", "expiration_date"),
    ("2024/05/06", "expiration_date"),
    ("2025/08/17", "expiration_date"),
    ("2024/11/22", "expiration_date"),
    ("2023/04/03", "expiration_date"),
    ("2025/06/28", "expiration_date"),
    ("2024/03/08", "expiration_date"),
    ("2023/02/14", "expiration_date"),
    ("2025/04/29", "expiration_date"),
    ("2024/01/05", "expiration_date"),
    ("2023/08/23", "expiration_date"),
    ("2025/07/11", "expiration_date"),
    ("2024/06/19", "expiration_date"),
    ("2023/05/25", "expiration_date"),
    ("2025/10/07", "expiration_date"),
    ("2024/02/11", "expiration_date"),
    ("2023/01/17", "expiration_date"),
    ("2025/09/26", "expiration_date"),
    ("2024/04/01", "expiration_date"),
    ("2023/03/15", "expiration_date"),
    ("2025/01/24", "expiration_date"),
    ("2024/12/30", "expiration_date"),
    ("2023/11/14", "expiration"),
    ("2024/02/20", "expiration_date"),
    ("2023/07/03", "expiration_date"),
    ("2023/07/03", "expiration_date"),
("2023/08/15", "expiration_date"),
("2025/01/12", "expiration_date"),
("2024/06/23", "expiration_date"),
("2023/09/30", "expiration_date"),
("2025/11/21", "expiration_date"),
("2024/07/05", "expiration_date"),
("2023/03/27", "expiration_date"),
("2025/02/14", "expiration_date"),
("2024/12/19", "expiration_date"),
("2028/07/29", "expiration_date"),
("MADISON AQUINO", "name"),
("SEBASTIAN GARCIA", "name"),
("AVERY SANTOS", "name"),
("LIAM SANTIAGO", "name"),
("CHARLOTTE CRUZ", "name"),
("DANIEL REYES", "name"),
("MIA DELA ROSA", "name"),
("1990/01/15", "birthday"),
("1991/02/28", "birthday"),
("1992/03/17", "birthday"),
("1993/04/24", "birthday"),
("1994/05/12", "birthday"),
("1995/06/30", "birthday"),
("1996/07/18", "birthday"),
("1997/08/25", "birthday"),
("1998/09/19", "birthday"),
("1999/10/21", "birthday"),
("2000/11/11", "birthday"),
("2001/12/05", "birthday"),
("2002/01/20", "birthday"),
("2003/02/14", "birthday"),
("2004/03/26", "birthday"),
("2005/04/13", "birthday"),
("1990/02/11", "birthday"),
("1991/03/24", "birthday"),
("1992/04/10", "birthday"),
("1993/05/22", "birthday"),
("1996/12/23", "birthday")

]


@svm_bp.route('/violators', methods=['GET', 'POST'])
def violators():
    if request.method == 'POST':
        session['submitted'] = True

        # Database connection and cursor
        db_connection = get_db_connection()
        cursor = db_connection.cursor()

        # Get the latest extracted_id
        cursor.execute("SELECT MAX(id) FROM reports")
        largest_id = cursor.fetchone()[0]

        if largest_id is None:
            new_id = 1
        else:
            cursor.execute("SELECT tct_number FROM reports WHERE id = %s", (largest_id,))
            existing_tct_number = cursor.fetchone()[0]
            new_id = int(existing_tct_number.split('-')[1]) + 1

        generated_id = 'TCT-' + str(new_id).zfill(5)
        tct_number = generated_id

        # Retrieve form data
        extracted_text = request.form['extracted_text']

        # Parse JSON string into dictionary
        data = json.loads(extracted_text)

        # Prepare data for SVM model
        texts, labels = zip(*data_sets)
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(texts)

        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.3, random_state=42)

        # Train SVM classifier
        svm_classifier = SVC(kernel='linear')
        svm_classifier.fit(X_train, y_train)

        # Extract values for prediction and ensure they are strings
        values = [str(value) for value in data.values()]

        # Predict for new texts
        new_X = vectorizer.transform(values)
        predictions = svm_classifier.predict(new_X)
        
        predicted_license_number = ""
        predicted_expiration_date = ""
        predicted_birthday = ""
        # Log predictions
        
        print("Predictions:", predictions)
        for text, pred_label in zip(values, predictions):
            print(f"{text} -> Predicted category: {pred_label}")
            if pred_label == 'name':
                predicted_name = text
            elif pred_label == 'license_number':
                predicted_license_number = text
            elif pred_label == 'expiration_date':
                predicted_expiration_date = text
            elif pred_label == 'birthday':
                predicted_birthday = text
       
        # Get image data from the form
        image = request.form.get('image_data')

        # Generate random filename with date
        random_filename = f"{tct_number}_{str(uuid.uuid4())[:8]}.png"
        image_binary = base64.b64decode(image.split(',')[1])

        # Save the image
        image_path = os.path.join('static/extracted_images', random_filename)
        with open(image_path, 'wb') as f:
            f.write(image_binary)

        image_data = random_filename

        # Insert data into the database
        cursor.execute("INSERT INTO extracted_data (extracted_text, tct_number, image_data,name,license_number,expiration_date,date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s)", (extracted_text, tct_number, image_data,predicted_name,predicted_license_number,predicted_expiration_date,predicted_birthday))
        db_connection.commit()

        cursor.execute("INSERT INTO reports (tct_number, name,license_number) VALUES (%s, %s,%s)", (tct_number,predicted_name,predicted_license_number))
        # Close database connection
        cursor.close()
        db_connection.close()

        return redirect(url_for('svm.violators', tct_number=tct_number))

    tct_number = request.args.get('tct_number')
    return render_template('violators-form.html', tct_number=tct_number)