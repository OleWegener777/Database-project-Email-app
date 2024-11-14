-- Active: 1729165252124@@127.0.0.1@5432@management
ALTER TABLE invoices
ADD COLUMN Status BOOLEAN DEFAULT False; 

ALTER TABLE invoices
RENAME COLUMN Status TO EmailStatus;

ALTER TABLE invoices
ADD COLUMN Email_invoice_type VARCHAR(10) DEFAULT 'PDF' ;

ALTER TABLE invoices
ADD COLUMN Email_invoice BOOLEAN DEFAULT False;

ALTER TABLE invoices
ADD COLUMN file VARCHAR (20);

UPDATE invoices
SET file = invoice_id || '.pdf'

SELECT * FROM invoices
ORDER BY invoice_id;

SELECT * FROM customers
ORDER BY id;

## RESET:

UPDATE invoices
SET emailstatus = False
;

#######

SELECT invoice_id, customer_id, name FROM invoices JOIN customers ON invoices.customer_id = customers.id WHERE emailstatus = False;

UPDATE customers
SET email = 'ole.wegener@dci-student.org'
;