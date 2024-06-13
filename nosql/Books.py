# Import the necessary modules
from pymongo import MongoClient
from neo4j import GraphDatabase

# Define the MongoDBLibrary class
class MongoDBLibrary:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client["Data_Library"]
        self.books_collection = self.db["books"]

    def add_book(self, title, author, category, cover, quantity, about):
        self.books_collection.insert_one({
            "title": title,
            "author": author,
            "category": category,
            "cover": cover,
            "quantity": quantity,
            "about": about
        })

# Create an instance of MongoDBLibrary
mongo_lib = MongoDBLibrary("mongodb://localhost:27017/")

#Neo4j
# Define Neo4j connection details
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "Movies2024"

# Neo4j driver
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))


books = [
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "category": "Fiction",
        "cover": "https://img1.od-cdn.com/ImageType-400/0211-1/%7B4FD7EF4F-B5AA-4C6A-85E7-C431E5A46496%7DIMG400.JPG",
        "quantity": 5,
        "about": "A young girl named Scout Finch grows up in the racially charged atmosphere of 1930s Alabama, learning about justice and empathy."
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "category": "Classics",
        "cover": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmDonjr6DwyqEiQjMrFD3RK-EM7JvWdRLJTOg_NMLgzA&s",
        "quantity": 3,
        "about": "The story of the mysterious millionaire Jay Gatsby and his obsession with the beautiful Daisy Buchanan."
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "category": "Dystopian",
        "cover": "https://booksondemand.ma/cdn/shop/products/1_dc7d5ded-eff3-48dd-b8a9-14ea9d25104d.jpg?v=1668004764",
        "quantity": 8,
        "about": "A chilling depiction of a totalitarian regime that uses surveillance, censorship, and control to maintain power."
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "category": "Classics",
        "cover": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3b8D0F7dOGLYrZ8gB9HgmljY1wmt9NykLF3aaFen9mg&s",
        "quantity": 4,
        "about": "The story of Holden Caulfield, a teenage boy who leaves his prep school and experiences the challenges of adolescence."
    },
    {
        "title": "Animal Farm",
        "author": "George Orwell",
        "category": "Satire",
        "cover": "https://booksondemand.ma/cdn/shop/products/71JUJ6pGoIL-min.jpg?v=1631701297",
        "quantity": 6,
        "about": "A satirical tale of a group of farm animals who overthrow their human owner, only to become oppressed by their own kind."
    },
    {
        "title": "Lord of the Flies",
        "author": "William Golding",
        "category": "Fiction",
        "cover": "https://images.penguinrandomhouse.com/cover/9780399537424",
        "quantity": 7,
        "about": "A group of boys stranded on a deserted island descend into savagery as they struggle for survival."
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "category": "Romance",
        "cover": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSZQJgJfVHegtGSwkAs23u2QLJHinWTEQR530udNUHoTQ&s",
        "quantity": 5,
        "about": "The story of Elizabeth Bennet and her romantic entanglements, exploring themes of class and social standing."
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "category": "Fantasy",
        "cover": "https://i.ebayimg.com/images/g/HW4AAOSwYDZgjoaO/s-l600.jpg",
        "quantity": 10,
        "about": "Bilbo Baggins, a hobbit, embarks on an unexpected journey to help a group of dwarves reclaim their homeland."
    },
    {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "category": "Dystopian",
        "cover": "https://booksondemand.ma/cdn/shop/products/3-min.jpg?v=1614522058",
        "quantity": 6,
        "about": "A futuristic society where humans are genetically engineered and conditioned for their roles, exploring themes of freedom and control."
    },
    {
        "title": "The Diary of a Young Girl",
        "author": "Anne Frank",
        "category": "Biography",
        "cover": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyXxhlk2Rgy-W5PpaR_vPfNMvSn9gljXRfEXEn_Cl_Hg&s",
        "quantity": 3,
        "about": "The poignant diary of Anne Frank, a Jewish girl hiding from the Nazis during World War II."
    },
    {
        "title": "The Hunger Games",
        "author": "Suzanne Collins",
        "category": "Dystopian",
        "cover": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.overdrive.com%2Fmedia%2F859111%2Fthe-hunger-games&psig=AOvVaw0kpyOqZetjcqZcWWY3Oaj0&ust=1717164105422000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCJCkmPfEtYYDFQAAAAAdAAAAABAJ",
        "quantity": 9,
        "about": "In a dystopian future, Katniss Everdeen must fight for survival in the brutal Hunger Games, a televised spectacle."
    }, 
    {
        "title": "The Book Thief",
        "author": "Markus Zusak",
        "category": "Historical Fiction",
        "cover": "https://images.booksense.com/images/207/842/9780375842207.jpg",
        "quantity": 4,
        "about": "A young girl living in Nazi Germany finds solace in stealing books and sharing them with others."
    },
    {
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J.K. Rowling",
        "category": "Fantasy",
        "cover": "https://booksondemand.ma/cdn/shop/products/81YOuOGFCJL-min.jpg?v=1609447821",
        "quantity": 12,
        "about": "A young boy discovers he is a wizard and attends a magical school, where he makes friends and enemies."
    },
    {
        "title": "Harry Potter and the Chamber of Secrets",
        "author": "J.K. Rowling",
        "category": "Fantasy",
        "cover": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQEtKq2bweD0u0t3Jj9uN_yBW7Udd1p1eJymEhzQyqPqg&s",
        "quantity": 11,
        "about": "Harry Potter returns for his second year at Hogwarts, where a hidden chamber is opened and students are petrified."
    },
    {
        "title": "Harry Potter and the Prisoner of Azkaban",
        "author": "J.K. Rowling",
        "category": "Fantasy",
        "cover": "https://prodimage.images-bn.com/pimages/9781338815283_p0_v6_s1200x630.jpg",
        "quantity": 13,
        "about": "Harry learns about the escape of Sirius Black, a prisoner believed to be after him, while discovering more about his past."
    },
    {
        "title": "Harry Potter and the Goblet of Fire",
        "author": "J.K. Rowling",
        "category": "Fantasy",
        "cover": "https://m.media-amazon.com/images/I/91SI2owt1XL._AC_UF1000,1000_QL80_.jpg",
        "quantity": 15,
        "about": "Harry is mysteriously entered into the Triwizard Tournament, facing dangerous challenges and uncovering dark plots."
    },
    {
        "title": "Harry Potter and the Order of the Phoenix",
        "author": "J.K. Rowling",
        "category": "Fantasy",
        "cover": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ2YzZW-9Kv30wyMHnOFkfaOD2NfX0aN0bIP0aFcg_5nQ&s",
        "quantity": 14,
        "about": "Harry forms a secret student group to oppose the authoritarian regime at Hogwarts and prepares for an impending battle."
    },
    {
        "title": "Harry Potter and the Half-Blood Prince",
        "author": "J.K. Rowling",
        "category": "Fantasy",
        "cover": "https://m.media-amazon.com/images/I/61sXBXmAWML._AC_UF1000,1000_QL80_.jpg",
        "quantity": 16,
        "about": "Harry discovers an old potions book with helpful annotations and uncovers more about Voldemort's dark past."
    },
    {
        "title": "Harry Potter and the Deathly Hallows",
        "author": "J.K. Rowling",
        "category": "Fantasy",
        "cover": "https://m.media-amazon.com/images/I/91VsRHjTY-L._AC_UF1000,1000_QL80_.jpg",
        "quantity": 17,
        "about": "Harry, Ron, and Hermione go on a mission to destroy Voldemort's Horcruxes and save the wizarding world."
    },
    {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "category": "Adventure",
        "cover": "https://m.media-amazon.com/images/I/61HAE8zahLL._AC_UF1000,1000_QL80_.jpg",
        "quantity": 8,
        "about": "A shepherd named Santiago travels from Spain to Egypt in search of a treasure, learning valuable life lessons along the way."
    }
]
books.extend([
    {
        "title": "Good Omens",
        "author": ["Neil Gaiman", "Terry Pratchett"],
        "category": "Fantasy",
        "cover": "https://fr.web.img4.acsta.net/pictures/19/02/14/16/18/3453995.jpg?coixp=51&coiyp=27",
        "quantity": 5,
        "about": "An angel and a demon team up to prevent the apocalypse."
    },
    {
        "title": "The Long Earth",
        "author": ["Terry Pratchett", "Stephen Baxter"],
        "category": "Science Fiction",
        "cover": "https://images-na.ssl-images-amazon.com/images/I/51QK33vRUbL._SX324_BO1,204,203,200_.jpg",
        "quantity": 4,
        "about": "A novel about parallel worlds and exploration."
    },
    {
        "title": "The Talisman",
        "author": ["Stephen King", "Peter Straub"],
        "category": "Horror",
        "cover": "https://images-na.ssl-images-amazon.com/images/I/51W6b+SR8lL._SX321_BO1,204,203,200_.jpg",
        "quantity": 3,
        "about": "A boy's journey through a parallel world to save his dying mother."
    },
    {
        "title": "The Rithmatist",
        "author": ["Brandon Sanderson", "Ben McSweeney"],
        "category": "Fantasy",
        "cover": "https://images-na.ssl-images-amazon.com/images/I/51XfGkQrdQL._SX329_BO1,204,203,200_.jpg",
        "quantity": 6,
        "about": "A story about a boy in a world where chalk drawings can come to life."
    },
    {
        "title": "The Cuckoo's Calling",
        "author": ["Robert Galbraith", "J.K. Rowling"],
        "category": "Mystery",
        "cover": "https://images-na.ssl-images-amazon.com/images/I/51+T3CHGRWL._SX323_BO1,204,203,200_.jpg",
        "quantity": 5,
        "about": "A private detective investigates a supermodel's suicide."
    },
    {
        "title": "The Expanse",
        "author": ["James S.A. Corey"],
        "category": "Science Fiction",
        "cover": "https://images-na.ssl-images-amazon.com/images/I/51l1W2uEhPL._SX331_BO1,204,203,200_.jpg",
        "quantity": 8,
        "about": "A series about a space opera involving the crew of the spaceship Rocinante."
    },
    {
        "title": "House of Leaves",
        "author": ["Mark Z. Danielewski", "Zampanò"],
        "category": "Horror",
        "cover": "https://images-na.ssl-images-amazon.com/images/I/51ymDh3eTQL._SX331_BO1,204,203,200_.jpg",
        "quantity": 3,
        "about": "A family discovers something is terribly wrong with their house."
    }
])

# Define a function to add a book and its author to Neo4j, and create relationships
def add_book_to_neo4j(book):
    with driver.session() as session:
        for author in book['author']:
            # Create or match the book node
            session.run(
                """
                MERGE (b:Book {title: $title, category: $category, cover: $cover, quantity: $quantity, about: $about})
                """,
                title=book['title'],
                category=book['category'],
                cover=book['cover'],
                quantity=book['quantity'],
                about=book['about']
            )
            
            # Create or match the author node
            session.run(
                """
                MERGE (a:Author {name: $author})
                """,
                author=author
            )
            
            # Create the "WROTE" relationship between the author and the book
            session.run(
                """
                MATCH (b:Book {title: $title})
                MATCH (a:Author {name: $author})
                MERGE (a)-[:WROTE]->(b)
                """,
                title=book['title'],
                author=author
            )

        # Create the "SAME_GENRE" relationship between books of the same genre
        session.run(
            """
            MATCH (b1:Book {title: $title})
            MATCH (b2:Book {category: $category})
            WHERE b1 <> b2
            MERGE (b1)-[:SAME_GENRE]->(b2)
            """,
            title=book['title'],
            category=book['category']
        )

        # Create the "WROTE_SAME_GENRE" relationship between authors of books in the same genre
        session.run(
            """
            MATCH (a1:Author)-[:WROTE]->(:Book {category: $category})<-[:WROTE]-(a2:Author)
            WHERE a1 <> a2
            MERGE (a1)-[:WROTE_SAME_GENRE]->(a2)
            """,
            category=book['category']
        )

        # Create the "CO_WRITING" relationship between authors who wrote the same book
        authors = book['author']
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                session.run(
                    """
                    MATCH (a1:Author {name: $author1})
                    MATCH (a2:Author {name: $author2})
                    MERGE (a1)-[:CO_WRITING]->(a2)
                    """,
                    author1=authors[i],
                    author2=authors[j]
                )


#Add each book to Neo4j
for book in books:
    add_book_to_neo4j(book)


# Add each book to the MongoDB collection
for book in books:
        mongo_lib.add_book(book['title'], book['author'], book['category'], book['cover'], book['quantity'], book['about'])

