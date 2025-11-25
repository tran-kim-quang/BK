import hashlib
def generate_course_id(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()
print(generate_course_id("https://bkacad.com/khoa-hoc-va-chuyen-nganh.html"))