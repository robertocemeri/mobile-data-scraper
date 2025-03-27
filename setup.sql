create table if not exists target_sites (
    id uuid default uuid_generate_v4() primary key,
    url text not null,
    topic text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Insert some initial data
insert into target_sites (url, topic) values
    ('https://www.swisscom.ch/en/residential.html', 'Mobile'),
    ('https://www.sunrise.ch/en/home', 'Mobile'),
    ('https://www.salt.ch/en', 'Mobile');