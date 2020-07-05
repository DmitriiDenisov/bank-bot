insert into balances (customer_id, usd_bal, eur_bal, aed_bal) values (1, -4, 120, 0)
select * from balances


ALTER TABLE balances ADD CONSTRAINT fk_balances FOREIGN KEY (customer_id) REFERENCES customers (id);


insert into customers (first_name, second_name, nickname_telegram, join_date) VALUES ('Dmitry', 'Denisov', 'ssf', '2020-01-06')
insert into balances (customer_id, usd_bal, eur_bal, aed_bal) values (8, 0, 1030, 0)
insert into transactions (customer_id_from, customer_id_to, usd_amt, eur_amt, aed_amt) VALUES (10, 6, 0, 3, 0)
insert into transactions (customer_id_from, customer_id_to, usd_amt, eur_amt, aed_amt) VALUES (6, 5, 0, 0.1, 0)

delete from customers;
delete from balances;
delete from transactions;

delete from customers where id=6;

select * from transactions;

ALTER TABLE balances ADD CONSTRAINT fk_balances FOREIGN KEY (customer_id) REFERENCES customers (id) on delete cascade;
ALTER TABLE transactions ADD CONSTRAINT fk_transactions_to FOREIGN KEY (customer_id_to) REFERENCES customers (id) on delete set null ;
ALTER TABLE transactions ADD CONSTRAINT fk_transactions_from FOREIGN KEY (customer_id_from) REFERENCES customers (id) on delete set null ;



alter table transactions drop constraint fk_transactions_to_2;


