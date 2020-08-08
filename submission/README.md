My CS50 final project is a personal project that I have wanted for a while and have finally had an excuse to create. I made a link shortener where user registration
is controlled by administrators and is a "private" website - all users must be logged in to view, edit, and remove links, but all short links may be accessed by the
public.

When logged out, a user will only be able to see the login screen, unless they are trying to go to a short link (i.e. http://<address>/<link code>) Clicking on a
short link from any source will result in a click counter increasing as well. The user that owns the link will be able to see the click count.

Upon logging in, the user will be presented with a home screen consisting of a list of their links. There is a table that shows each link's shortened address,
its "real" address, the number of times it's been clicked, and when it was created. There is also a radio button next to each link that ties into a form surrounding
the table. There are also two buttons below the table, one directing to a page to add a new link, and one allowing the user to remove a link. Upon selecting one of
the links by selecting its corresponding radio button, the link may be permanently deleted by simply pressing the button.

To add a new link, there is a button on the navbar and a button on the homepage beneath the table of links. When the user navigates to the page to add a link, they
will be presented with two text fields - one for the link, and one for the custom code that will make up the path of the shortened link. The link itself will be
heavily validated with regex and the scheme will be standardized - that is, https will turn into http, no scheme will turn into http, etc. to standardize the link.
This way, instead of having to enter https://google.com, the user can simply enter google.com.

Also on the navigation bar are a change password link and a logout link. These two links allow for users to change their passwords and delete the session,
respectfully.

Finally, for accounts that are labeled "administrator" (as determined through manually editing the database), there is an extra page called "Manage Users".
Due to the private nature of the site, I only want approved people to be able to create links. Thus, this admin-only page is where users are registered and removed
from the website. Similar to the homepage displaying the links, there is a table of usernames with radio buttons next to them. Any administrator accounts are clearly
marked and the radio buttons are disabled, signifying they cannot be removed. Beneath the table are two buttons - a button to register a new user and a button to
delete the selected user. The registration screen is simple, providing username, password, and confirmed password fields. Once registered, a user can immediately log
in and start creating links. Upon deletion, a user AND ALL THEIR LINKS will be deleted. Thus, this method of managing users helps to maintain a private site.


Thank you so much for this course! I have learned a lot and enjoyed it very much :)
- Ian