package queryComplaints;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import twitter4j.Query;
import twitter4j.QueryResult;
import twitter4j.Status;
import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;


public class ComplaintQuery {
	
	//Finding twitter id so that query isn't returning the same results
	static long lastID = 0L;
	static long firstID = 0L;
	
	public static void collect()
	{
		
		//Don't query twitter while the database is being updated 
		//if (!CrimeData.isCrimeUpdated)
		//{
			//return;
		//}
		
		System.out.println("Complaint Query Start");
		//access the twitter API using your twitter4j.properties file
		Twitter twitter = TwitterFactory.getSingleton();
				
		try
		{
		
		//creating a new search
		Query query = new Query("#LouComplaint @LouMetroBot -RT");
	
		setupSearchQuery(query, firstID, lastID);
	
		//Get the results from the search
		QueryResult result;
	
		//Collecting tweets to put into arraylist
		List<Status> tweets;
	
		//Collecting IDs to find lowest and highest status IDs
		ArrayList<Long> IDs = new ArrayList<Long>();
	    			    			
		do
		{	
			//Query Twitter
			result = twitter.search(query);
		
			tweets = result.getTweets();
		
			//For each twitter status that matches our query we log it in the log file
			for (Status status : tweets)
			{
				//Write to csv file
				WritingToFile.CSVFile(TwitterJSON.fileLocation, status.getText(), status.getUser().getScreenName(), status.getCreatedAt().toString(), tweetCleanup(status.getText()), "TWITTER");
			
							 
				//Add to ID arraylist
				IDs.add(status.getId() + 'L');
			}
		
			//Checking to see if there are more pages
			query = result.nextQuery();
		
			//Checking rate limit and will go to sleep if rate limit is reached
			checkRateLimit(result);
		}
		while (result == null || result.hasNext()); //we do this till the query is empty
		
		//if no new tweets are found, no need to collect new IDs
				if (IDs.size() > 0)
				{
					//Sorts from smallest to biggest
					Collections.sort(IDs);
			
					lastID = IDs.get(0) + 'L';
					firstID = IDs.get((IDs.size() - 1)) + 'L';
					
					//If new tweets have been found, run python code to convert the csv file to json
					Runtime.getRuntime().exec("cmd /c start runScript.bat");
									
				}
	
			System.out.println("Complaint Query Done"); //Help with Debug
		
		}
		
		catch (TwitterException tex)
	    {
	    	WritingToFile.LogError(tex.getExceptionCode(), tex.getErrorMessage());
	    	WritingToFile.LogError(tex.getMessage(), WritingToFile.exceptionStacktraceToString(tex));
	    	WritingToFile.LogError(tex.getLocalizedMessage(),"TESTING");
	    	
	    }
		
		catch (Exception ex)
		{
			WritingToFile.LogError(ex.toString(), WritingToFile.exceptionStacktraceToString(ex));
		}

}


private static void checkRateLimit(QueryResult result)
{
   //If we go over our rate limit
   if (result.getRateLimitStatus().getRemaining() <= 0)
   {
	   try
	   {
		  Thread.sleep(result.getRateLimitStatus().getSecondsUntilReset() * 1000);
         
	   } 
	   catch (Exception e) 
	   {
            e.printStackTrace();
            throw new RuntimeException(e);
       }
   }
}

private static void setupSearchQuery(Query query, long firstID, long lastID)
{
   
   	//Only looking for recent tweets not popular ones
	query.setResultType(Query.RECENT);
	
	//Ten tweets per page (Doubt its necessary but nevertheless)
	query.setCount(10);
				
	//Making sure we don't get the same tweets over and over again.
	if (firstID != 0L)
		query.setSinceId(firstID + 'L');
					
}

private static String tweetCleanup (String status)
{
   //Remove Hashtags from Tweets
   status = status.replaceAll("#[^\\s]*", "");
   
   //Remove URLs in Tweet
   status = status.replaceAll("http[^\\s]*", "");
   
   //Remove @UserNames from Tweet Text
   status = status.replaceAll("@[^\\s]*", "");
   
   //Remove commas and spaces that could interfere with the search
   status = status.replace(",", "");
   status = status.replace("\n", "").replace("\r", "");
   //status = status.replaceAll("\\s+", "");
   
   return status;
}

	

}
