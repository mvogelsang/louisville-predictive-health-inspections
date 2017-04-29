package queryComplaints;
import java.io.File;
import java.io.FileOutputStream;

import java.io.PrintWriter;
import java.nio.file.Files;



public class TwitterJSON {
	
	//Setting location of the file.
	public static String fileLocation = "ComplaintLog.csv";

	
	public static void main(String[] args) 
	{		
		
		//We delete the file if the program has been reset so that we don't have duplicate tweets in the file
		File file = new File(fileLocation);
		
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
				sb.append('\n');
							
				pw.write(sb.toString());
				pw.close();
						
			}
		} 
		catch (Exception e) 
		{
			//Do Nothing
		}
		
		new ComplaintQuery();
		
		ComplaintQuery.collect();
		
		System.exit(0);

	}
	   

}
