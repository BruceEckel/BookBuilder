if exist pylint-out.txt del pylint-out.txt
call pylint ebook_generators.py >> pylint-out.txt
call pylint examples.py >> pylint-out.txt
call pylint util.py >> pylint-out.txt
call pylint validate.py >> pylint-out.txt
call pylint scripts\book_builder.py >> pylint-out.txt
call pylint scripts\generate_output.py >> pylint-out.txt
call subl ebook_generators.py
call subl examples.py
call subl util.py
call subl validate.py
call subl scripts\book_builder.py
call subl scripts\generate_output.py
call subl pylint-out.txt
call subl C:\Users\bruce\.pylintrc
