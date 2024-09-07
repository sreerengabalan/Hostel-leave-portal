db=db.getSiblingDB("user_login");


db.users.insertOne({
    "Name": "Admin",
    "Email": "admin@gmail.com",
    "password": "$pbkdf2-sha256$29000$d24NgfBe632v1ZozpjQGQA$qD2FhDNaWbBDKg4I7n2f.JsMGHCim.me0ND6p8PsGTs"
  });
  
