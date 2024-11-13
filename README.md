# Cyber Security Base 2024: Project 1

For my project, I developed a minimalist blogging platform. The primary functionalities include user sign-up, post publishing, commenting on posts, and searching for posts by keyword. Users can also edit or delete their posts and comments. My focus in development was solely on the back-end, so the front-end was intentionally kept basic and unstyled.

I purposefully incorporated six distinct vulnerabilities from the 2021 OWASP Top Ten list, which are common issues in modern web applications. Here’s a breakdown of each flaw, why it’s a problem, and how it can be fixed.

## Installation instructions
1. Install required [dependencies ](https://cybersecuritybase.mooc.fi/installation-guide)
2. Clone repository
3. Execute `py manage.py migrate`  in terminal
4. Execute `py manage.py runserver`  in terminal
5. Access application by typing `localhost:8000` in browser
6. Create an account (sign up)
7. Close the server with CTRL+C in the terminal once finished

## Flaws

### Flaw 1: Security Misconfiguration (A05:2021)
- **Source**: `/notsosecureapp/notsosecureapp/settings.py#L26`
 
- **Description**: The application’s settings file currently has debug mode enabled, which is common during development to display detailed error messages and system information that assists with troubleshooting. However, if debug mode (`DEBUG = True`) is left enabled in a production environment, it becomes a significant security risk. Debug mode outputs sensitive data about the server and database configurations, user sessions, and routes, which can help attackers understand the system’s inner workings and plan their attacks accordingly. For instance, an attacker could use error tracebacks and SQL error messages to identify SQL queries and injection points.
 
- **Fix**: Before deploying the application to production, it’s essential to disable debug mode by setting `DEBUG = False` in the `settings.py` file (line 26).

### Flaw 2: Identification and Authentication Failures (A07:2021)
- **Source**: `/notsosecureapp/settings.py#L37` & `/notsosecureapp/securesessions.py`
 
- **Description**: In this application, session management is implemented with a custom session key generator in the `securesessions.py` file. This was meant to explore custom key generation for user sessions, but the generator used here creates session keys that are simple and predictable. Predictable session keys can be easily guessed or brute-forced, allowing attackers to hijack sessions, impersonate users, or perform unauthorized actions. Effective session management is crucial in developing web applications, as session IDs authenticate and protect user interactions with the server.
 
- **Fix**: To secure session handling, the `securesessions.py` file should be removed and line 37 in `settings.py` deleted so the application reverts to Django’s built-in session management. Django’s default session management is well-tested, and it generates secure, random session IDs that are challenging to predict. This also removes the burden of session security from developers, ensuring that user session data remains safe.

### Flaw 3: Insecure Design (A04:2021)
- **Source**: `/notsosecureapp/settings.py#L98`
 
- **Description**: The application’s current password policy does not enforce any strength requirements, allowing users to create weak passwords. Without a strong password policy, users may set passwords like "password" or "12345," which are easily guessable by attackers. An insecure design like this increases the risk of account compromise through brute-force attacks or credential stuffing, where attackers attempt to log in using common or previously breached passwords. Password policies that encourage stronger, unique passwords help protect user accounts and overall application security.
 
- **Fix**: Django provides a set of configurable password validators to enforce a robust password policy. These validators are commented out in the `settings.py` file (lines 100-111). To enable them, these lines need to be uncommented. With these validators active, users will need to create passwords that meet specific length, complexity, and uniqueness criteria, greatly reducing the likelihood of weak passwords and account compromises.

### Flaw 4: Cryptographic Failures (A02:2021)
- **Source**: `/main/views.py#L50` & `/main/templates/create_post.html#L12`
 
- **Description**: The `create_post()` function in `views.py` currently sends data to the server using a GET request instead of a POST request. GET requests append data to the URL, making it easily visible and accessible to anyone monitoring traffic or viewing browser history. This exposure of sensitive data in URLs could inadvertently leak user-generated content, especially if users include private or confidential information. Proper handling of sensitive data should ensure that it isn’t visible in URLs, especially for actions like creating posts, logging in, or submitting forms.
 
- **Fix**: To address this flaw, the form in `create_post.html` needs to be updated to use the `POST` method instead of `GET` by changing `method="get"` to `method="post"` on line 14. Likewise, in `views.py` on line 57, `request.GET` needs to be changed to `request.POST` to ensure data is securely transmitted. POST requests encapsulate data in the request body, protecting it from unnecessary exposure.

### Flaw 5: Broken Access Control (A01:2021)
- **Source**: `/main/views.py#L87`, `#L130`, `#L143`
 
- **Description**: Currently, the application lacks sufficient access control, allowing any logged in user to edit or delete any post or comment, even if they are not the author. Without access control, unauthorized users can manipulate or delete other users’ content. This could lead to data tampering and privacy breaches. Effective access control is essential for any multi-user application to ensure users can only access and modify their own content.
 
- **Fix**: In `views.py`, I’ve commented out code on lines 87-88, 130-131, and 143-144 that checks if the current user is the author of a post or comment before allowing modifications or deletion. Uncommenting these lines will restore this validation. Additionally, to ensure that unauthorized users don’t see edit/delete buttons in the UI on other users' posts, conditional statements in `edit_post.html` (line 18) and `post_detail.html` (lines 19 and 37) need to be uncommmented. This way, only authors of posts or comments can view and use these options, aligning front-end and back-end access control.

### Flaw 6: Injection (A03:2021)
- **Source**: `/main/views.py#L111` & `/main/templates/post_detail.html#L18, #L32`
 
- **Description**: The application is vulnerable to cross-site scripting (XSS) attacks through the comment section. XSS attacks occur when attackers inject malicious scripts into web pages, which execute in the context of another user’s session. In this case, users can enter JavaScript code, like `<script>alert("XSS ATTACK")</script>`, into a comment they publish. The script would execute in the browser of anyone viewing the page, potentially compromising user data or session information. By default, Django protects against XSS, but the use of the `|safe` filter bypasses this protection, creating a security hole.
 
- **Fix**: To secure against XSS,`@csrf_exempt` in `views.py` (line 111) needs to be removed, ensuring that Django’s CSRF protection is enabled for the comment form. Additionally, the CSRF token in `post_detail.html` on line 32 needs to be uncommented, which will embed the CSRF token in the comment form, preventing unauthorized requests. Lastly, the `|safe` tag from line 18 in `post_detail.html` should be removed. Without `|safe`, Django will automatically escape HTML characters, preventing user-generated content from containing executable code and thus mitigating the XSS risk.
