/* STACK EXCHANGE DATA EXPLORER QUERIES */


/*
https://data.stackexchange.com/
Choose a site
Click "Compose Query"
*/


/**********/
/* 10 oldest users : display name, creation date, user id */
/**********/


SELECT DisplayName, CreationDate, Id
FROM
(
	SELECT TOP 10 *
	FROM Users
	ORDER BY CreationDate
) T1
ORDER BY CreationDate


/**********/
/* 10 oldest users : display name, creation date, user id, number of posts */
/**********/


SELECT	DisplayName,
	CreationDate,
	Id,
	CAST(0 as int) AS NumPosts
INTO	#temp
FROM
(
	SELECT TOP 10 *
	FROM Users
	ORDER BY CreationDate
) T1

SELECT	OwnerUserId, COUNT(DISTINCT Id) AS nbposts
INTO	#temp2
FROM	Posts
WHERE	OwnerUserId IN (SELECT Id FROM #temp)
GROUP BY OwnerUserId

UPDATE	#temp
SET	#temp.NumPosts = #temp2.nbposts
FROM	#temp
INNER JOIN #temp2
ON	#temp.Id = #temp2.OwnerUserId

SELECT	*
FROM	#temp
ORDER BY Id


/**********/
/* 10 oldest users - 2 most recent posts for each : user id, post id, post creation date, post body */
/**********/


SELECT	TOP(10) Id
INTO	#temp
FROM	Users
ORDER BY CreationDate


SELECT	OwnerUserId,
	Id,
	CreationDate,
	Body
INTO	#temp2
FROM	Posts
WHERE	OwnerUserId IN (SELECT Id FROM #temp)

SELECT	OwnerUserId,
	Id,
	CreationDate,
	Body
FROM
(
	SELECT	OwnerUserId,
		Id,
		CreationDate,
		Body,
		DENSE_RANK() OVER (PARTITION BY OwnerUserId ORDER BY CreationDate DESC) AS DateRank
	FROM	#temp2
) T2
WHERE DateRank <= 2


/**********/
/* 10 most recent posts for user with id 7035 -  post id, creation date, body, score (stored), score (computed from votes table, number of upvotes - number of downvotes) */
/**********/


SELECT	TOP(10) Id
INTO	#temp
FROM	Posts
WHERE	OwnerUserId = 7035
ORDER BY CreationDate DESC


SELECT	P.Id, P.CreationDate, P.Body, P.Score, T2.CalculatedScore
FROM	Posts P
INNER JOIN
(
	SELECT	Id,
		UpVotes - DownVotes as CalculatedScore
	FROM
	(
		SELECT	#temp.Id,
		COUNT(CASE WHEN Votes.VoteTypeId = 2 THEN 1 ELSE NULL END) AS UpVotes,
		COUNT(CASE WHEN Votes.VoteTypeId = 3 THEN 1 ELSE NULL END) AS DownVotes
		FROM	#temp
		LEFT JOIN Votes
		ON	#temp.Id = Votes.PostId
		GROUP BY #temp.Id
	) T1
) T2
ON P.Id = T2.Id


/**********/
