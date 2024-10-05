import sqlite3

# Function to connect to the database
def connect_to_db(db_name="tiktok.db"):
    conn = sqlite3.connect(db_name)
    return conn

# Function to create the tables
def create_tables(conn):
    cursor = conn.cursor()
    
    # Create the 'users' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            follower_count TEXT,
            following_count TEXT,
            like_count TEXT
        )
    ''')

    # Create the 'posts' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            post_id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_url TEXT NOT NULL,
            video_caption TEXT,
            author_username TEXT NOT NULL,
            FOREIGN KEY (author_username) REFERENCES users(user_id)
        )
    ''')

    conn.commit()

# Function to insert a user into the 'users' table
def insert_user(conn, follower_count, following_count, like_count):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (follower_count, following_count, like_count)
        VALUES (?, ?, ?)
    ''', (follower_count, following_count, like_count))
    conn.commit()

# Function to insert a post into the 'posts' table
def insert_post(conn, video_url, video_caption, author_username):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO posts (video_url, video_caption, author_username)
        VALUES (?, ?, ?)
    ''', (video_url, video_caption, author_username))
    conn.commit()

# Function to retrieve all users
def get_all_users(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    return cursor.fetchall()

# Function to retrieve all posts
def get_all_posts(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts')
    return cursor.fetchall()

# Function to retrieve posts by a specific username
def get_posts_by_author(conn, author_username):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE author_username = ?', (author_username,))
    return cursor.fetchall()

# Function to update follower count for a user
def update_follower_count(conn, user_id, new_follower_count):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET follower_count = ?
        WHERE user_id = ?
    ''', (new_follower_count, user_id))
    conn.commit()

# Function to delete a post by post_id
def delete_post(conn, post_id):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE post_id = ?', (post_id,))
    conn.commit()

def insert_multiple_posts(conn, posts_list):
    cursor = conn.cursor()
    
    # Preparing the data for batch insert
    posts_data = [(post['video_url'], post['video_caption'], post['author_username']) for post in posts_list]
    
    cursor.executemany('''
        INSERT INTO posts (video_url, video_caption, author_username)
        VALUES (?, ?, ?)
    ''', posts_data)
    
    conn.commit()

# Function to check if a video_url already exists in the posts table
def video_url_exists(conn, video_url):
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM posts WHERE video_url = ?', (video_url,))
    return cursor.fetchone() is not None

# Function to insert multiple posts with redundancy check
def insert_multiple_posts(conn, posts_list):
    cursor = conn.cursor()
    for post in posts_list:
        video_url = post['video_url']
        
        # Check if the video URL already exists in the database
        if not video_url_exists(conn, video_url):
            # Insert the post if the URL doesn't already exist
            cursor.execute('''
                INSERT INTO posts (video_url, video_caption, author_username)
                VALUES (?, ?, ?)
            ''', (video_url, post['video_caption'], post['author_username']))
        else:
            print(f"Post with video_url {video_url} already exists. Skipping insertion.")
    
    conn.commit()

# Example of how to use the functions
if __name__ == "__main__":
    conn = connect_to_db()
    create_tables(conn)
    conn.close()

    """
    
    
    # Example insertions
    insert_user(conn, 1000, 500, 20000)  # Inserting a user
    insert_post(conn, 'http://video.com/123', 'Check out this cool video', 'user1')  # Inserting a post

    # Retrieving data
    users = get_all_users(conn)
    print("Users:", users)

    posts = get_all_posts(conn)
    print("Posts:", posts)

    # Closing the connection
    conn.close()

    """

# Function to check if a video_url already exists in the posts table
def video_url_exists(conn, video_url):
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM posts WHERE video_url = ?', (video_url,))
    return cursor.fetchone() is not None

# Function to insert multiple posts with redundancy check
def insert_multiple_posts(conn, posts_list):
    cursor = conn.cursor()
    for post in posts_list:
        video_url = post['video_url']
        
        # Check if the video URL already exists in the database
        if not video_url_exists(conn, video_url):
            # Insert the post if the URL doesn't already exist
            cursor.execute('''
                INSERT INTO posts (video_url, video_caption, author_username)
                VALUES (?, ?, ?)
            ''', (video_url, post['video_caption'], post['author_username']))
        else:
            print(f"Post with video_url {video_url} already exists. Skipping insertion.")
    
    conn.commit()

# Function to retrieve all video URLs from the posts table
def get_all_urls(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT video_url FROM posts')
    urls = cursor.fetchall()
    
    # Extracting URLs from the tuples and returning a list of URLs
    return [url[0] for url in urls]


# Example usage:
if __name__ == "__main__":
    conn = connect_to_db()
    create_tables(conn)

    # Retrieving all posts to verify insertion
    all_posts = get_all_posts(conn)
    print("Posts:", all_posts)

    conn.close()