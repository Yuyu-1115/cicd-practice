INSERT OR IGNORE INTO users (
    full_name, 
    bday, 
    gender, 
    email, 
    phone, 
    address,
    city,
    states,
    postcode,
    university, 
    profession
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);