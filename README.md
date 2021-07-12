# contacts

To use this code install the following libraries using pip command:
```
starlette==0.15.0
uvicorn==0.14.0
```

Do not forget to change connection details of Posgresql. Find the following line in line 12, 23, 27 and change:
```
con = psycopg2.connect("user='username' password='password' host='localhost' port='5432'")
```

After installing them run the following command to run the script:
```
uvicorn routes:app --reload
```
