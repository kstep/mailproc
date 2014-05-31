mailproc
========

procmail in python

Procmail is very powerful, but it's configuration format is really terrible.

This program replaces it with Python, so you can put email processing rules to `~/.mailprocrc` in a nice pythonic way.

The script provides a set of modules (`subprocess`, `os`, `sys`) and variables (`message` and `mbox`
for current message being processed and current user's mailbox file), as well as helpers
(`default_process()` function for fallback processing),
so you can start writing your `~/.mailprocrc` file immediately without a lot of boilerplate code like bunch
of `import`s in the beggining.

All you have to do is just analyze `message` (an `email.message` object) and act on it, and call
`default_process(mbox, message)` if you want to fall back to default action.

Example:

```python
ATTACHMENTS_DIR = os.path.expanduser('~/mail')
LINK_RE = re.compile(r'(?:ht|f)tps?://\S+', re.I)

if message['content-type'].startswith('multipart/mixed'):
    mkdir_p(ATTACHMENTS_DIR)

    for msg in walk_message(message):
        if msg.get_content_type() not in ('text/plain', 'text/html'):
            filename = os.path.join(ATTACHMENTS_DIR,
                    os.path.realpath(os.path.sep + msg.get_filename())
                        .strip(os.path.sep)
                        .replace(os.path.sep, '-'))

            if not os.path.exists(filename):
                with open(filename, 'wb') as f:
                    f.write(msg.get_payload(decode=True))


elif 'download' in message['subject'].lower():
    subprocess.Popen(['/usr/bin/wget', '-P', os.path.expanduser('~/downloads'), '-i', '-', '-nc'],
        stdin=subprocess.PIPE
        ).communicate(
            '\n'.join(
                link.group(0) 
                for msg in walk_message(message)
                for link in LINK_RE.finditer(msg.get_payload(decode=True))
                if msg.get_content_type() in ('text/plain', 'text/html')
            ))

else:
    default_process(mbox, message)

```

Or you can use more strict/functional way if you like:

```python
@recipe(lambda m: m['content-type'].startswith('multipart/mixed'))
def save_attachments(mbox, message):
    pass
    
@recipe(lambda m: 'download' in m['subject'].lower())
def download_links_from_email(mbox, message):
    pass
```

In the second form you don't have to call `default_process()` manually, it will be called for you if none of your recipes match your message.

Example of opensmptd config (`/etc/smtpd/smtpd.conf`) to use mailproc:

```
accept from any for domain "home.kstep.me" alias <aliases> deliver to mda "/usr/local/bin/mailproc.py"
```
