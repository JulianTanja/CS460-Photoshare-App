/* this is for searching for new friends to add*/
SELECT U.first_name, U.last_name, U.email
FROM Users U
WHERE U.email REGEXP 'name'

/* this is for listing all of the friends of current user */
SELECT U.first_name, U.last_name, U.email
FROM Users U, (SELECT F.user_id2
FROM Users U, Friends F
WHERE U.user_id = '{0}' AND U.user_id = F.user_id1) AS AllF
WHERE U.user_id = AllF.user_id2

/* this is for listing all albums*/
SELECT A.name, A.date, A.albums_id
FROM Albums A

/* this is for getting photos from album id input */
SELECT P.data, P.photo_id, P.caption 
FROM Photos P, Albums A
WHERE A.albums_id = P.albums_id AND A.albums_id = '{0}'

/* this gets all albums from current user */
SELECT A.albums_id, A.name, A.date
FROM Albums A
WHERE A.user_id = '{0}'

/* this gets all photos from current user */
SELECT P.data, P.photo_id, P.caption
FROM Photos P
WHERE P.user_id = '{0}'

/* this deletes selected album id */
DELETE FROM Albums
WHERE albums_id = '{0}';

/* this deletes selected photo id */
DELETE FROM Photos
WHERE photo_id = '{0}';

/* this adds a new comment to userid photoid and text date */
INSERT INTO Comments (user_id, photo_id, text, date) VALUES ('{0}', '{1}', '{2}', '{3}')

/* this adds a like with userid photoid input */
INSERT INTO Likes (photo_id, user_id) VALUES ('{0}', '{1}')

/* this gets all the comments from a specific photo */
SELECT C.text, C.date, U.first_name
FROM Comments C, Photos P, Users U
WHERE P.photo_id = '{0}' AND C.user_id = U.user_id

/* this gets all likes from a specific photo */
SELECT COUNT(L.user_id)
FROM LIKES L
WHERE L.photo_id = '{0}'
GROUP BY L.photo_id

/* this gets all the comments from a specific photo from album id*/
SELECT C.text, C.date, U.first_name
FROM Comments C, Photos P, Users U, Albums A
WHERE A.albums_id = P.albums_id AND A.albums_id = '{0}' AND P.photo_id = C.photo_id AND C.user_id = U.user_id

/* this gets all likes from a specific photo from album id*/
SELECT COUNT(L.user_id)
FROM LIKES L, Albums A, Photos P
WHERE L.photo_id = P.photo_id AND A.albums_id = P.albums_id AND A.albums_id = '{0}'
GROUP BY L.photo_id

/* this gets all the uid and comments from a comment search */
SELECT U.first_name, U.last_name, U.email, C.text, COUNT(*) AS idcount
FROM Users U, Comments C
WHERE C.text REGEXP '{0}' AND C.user_id = U.user_id
GROUP BY U.user_id
ORDER BY idcount DESC

/* this gets all of the friends of the friends of current user, sorted by how many times they appear */
SELECT U.first_name, U.last_name, U.email, COUNT(*) AS idcount
FROM Friends F1, Friends F2, Users U
WHERE F1.user_id1 = '{0}' AND F1.user_id2 = F2.user_id1 AND F2.user_id2 = U.user_id
GROUP BY U.user_id
ORDER BY idcount DESC

/* this computes number of photos + number of comments from user only top 10 is returned */
SELECT U.first_name, U.last_name, U.email, COUNT(*) AS countall
FROM Users U, Comments C, Photos P
WHERE U.user_id = C.user_id AND C.user_id = P.user_id
GROUP BY U.user_id 
ORDER BY countall DESC
LIMIT 10

/* this creates a new tag with tag name */
INSERT INTO Tags (name) VALUES ('{0}')

/* this selects all availiable tag name and tag id */
SELECT T.name, T.tag_id
FROM Tags T

/* this inserts into tagged with tagid and photo id */
INSERT INTO Tagged (tag_id, photo_id) VALUES ('{0}', '{1}')

/* this gets all the photos from selected tagid and userid */
SELECT P.data, P.photo_id, P.caption 
FROM Photos P, Tagged T
WHERE P.photo_id = T.photo_id AND T.tag_id = '{1}' AND P.user_id = '{0}'

/* this gets all the photos from selected tagid */
SELECT P.data, P.photo_id, P.caption
FROM Photos P, Tagged T
WHERE P.photo_id = T.photo_id AND T.tag_id = '{0}'

/* most popular tags */
SELECT Ts.name, Ts.tag_id, COUNT(*) AS counted
FROM Tagged T, Tags Ts
WHERE T.tag_id = Ts.tag_id
GROUP BY T.tag_id 
ORDER BY counted DESC

/* this gets photo data id and caption from tag name search */
SELECT P.data, P.photo_id, P.caption
FROM Photos P, Tagged T, Tags Ts
WHERE Ts.name REGEXP '{0}' AND Ts.tag_id = T.tag_id AND P.photo_id = T.photo_id

/* most popular tags of current user*/
SELECT Ts.name, Ts.tag_id, COUNT(*) AS counted
FROM Tagged T, Tags Ts, Photos P
WHERE T.tag_id = Ts.tag_id AND P.photo_id = T.photo_id AND P.user_id = '{0}'
GROUP BY T.tag_id 
ORDER BY counted DESC

/* TODO */
/* ADD HOME BUTTONS FOR MOST PAGES           DONE*/ 
/* after deleting photo need to reset */
/* JUST NEED TO FIX DELETE WHEN DOUBLE PICTURES AND COMMENT WHEN DONE IT NEEDS TO REFRESH IT SELF AND NOT SHIT IT SELF*/
/* CANT COMMENT ON UR SELF ?????????????????????????*/
/* COMMENT 2 PIC SHITTING IT SELF