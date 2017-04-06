import java.io.File;
import java.io.FileOutputStream;

import java.io.PrintWriter;
import java.nio.file.Files;

import java.util.Timer;

import queryComplaints.ComplaintQuery;


public class TwitterJSON {

	public static void main(String[] args) 
	{
		//We delete the file if the program has been reset so that we don't have duplicate tweets in the file
		File file = new File("C:/inetpub/la/ComplaintLog.csv");
		
		try 
		{
			boolean result = Files.deleteIfExists(file.toPath());
			
			//If old file has been deleted, create new file with headers
			if (result)
			{
				PrintWriter pw = new PrintWriter(new FileOutputStream(file, true));
				StringBuilder sb = new StringBuilder();
				
				sb.append("Query_Date");
				sb.append(',');
				sb.append("Tweet_Sent");
				sb.append(',');
				sb.append("UserName");
				sb.append(',');
				sb.append("Raw_Message");
				sb.append(',');
				sb.append("Actual_Message");
				sb.append(',');
				sb.append("Twitter_Yelp");
				sb.append('\n');
							
				pw.write(sb.toString());
				pw.close();
						
			}
		} 
		catch (Exception e) 
		{
			//Do Nothing
		}
		
		Timer queryComplaints = new Timer();
    	
    	//Schedule to run every minute
		queryComplaints.schedule(new ComplaintQuery(), 0, 1000 * 60);
	}
	   

}
