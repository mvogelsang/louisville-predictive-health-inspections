using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Web;

namespace LouisvilleHealthInspections.DataContext
{
    public class GetJsonData
    {
        public string GetData(string fileLocation)
        {

            try
            {
                return File.ReadAllText(@fileLocation);
            }
            catch
            {
                return "File Not Found";
            }
        }
    }
    public class Tweet
    {
        public string Actual_Message { get; set; }
        public string Query_Date { get; set; }
        public string Raw_Message { get; set; }
        public string Tweet_Sent { get; set; }
        public string UserName { get; set; }
    }

    public class Tweets
    {
        public List<Tweet> tweets { get; set; }
    }

    public class Establishment
    {
        public long Establishment_Id { get; set; }
        public int Establishment_Rank { get; set; }
        public string Establishment_Name { get; set; }
    }

    public class Establishments
    {
        public List<Establishment> establishments { get; set; }
    }


}