from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Author, BookInstance, Genre
from urllib.parse import quote

import http.client



def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    books_list = Book.objects.all()
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'books_list': books_list,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


def book_detail(request, pk):
    """Get the information for a given book"""
    book = Book.objects.get(pk=pk)
    title = book.title
    author = book.author
    summary = book.summary
    genre = book.genre
    isbn = book.isbn
    instances = BookInstance.objects.filter(book=book)
    get_book_info(book)

    context = {
        'title' : title,
        'author': author,
        'summary' : summary,
        'genre': genre,
        'isbn': isbn,
        'bookinstance': instances,
        'book': book,
    }

    return render(request, 'catalog/book_detail.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 15

# class BookDetailView(generic.DetailView):
#     model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

def get_book_info(book):

    conn = http.client.HTTPSConnection("book-finder1.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "4329ef7408msh53be98e03ed8801p11ea0djsn9d388763b4fa",
        'X-RapidAPI-Host': "book-finder1.p.rapidapi.com"
        }
    book.title = quote(book.title)
    book_finder_url = f"/api/search?title={book.title}"
    conn.request("GET", book_finder_url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    book_info = data.decode("utf-8")
    print(book_info)
    
    return book_info