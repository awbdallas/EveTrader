drop table if exists reports;
create table reports (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);