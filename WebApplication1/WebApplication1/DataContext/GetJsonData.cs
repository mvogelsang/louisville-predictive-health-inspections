using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.IO;

namespace WebApplication1.DataContext
{
    public class GetJsonData
    {
        public JObject GetData()
        {
            return JObject.Parse(File.ReadAllText(@System.Configuration.ConfigurationManager.AppSettings["GetJsonString"]));
        }
    }

    public class Course
    {
        public string subject { get; set; }
        public string course_code { get; set; }
        public string sec { get; set; }
        public string title { get; set; }
        public string days { get; set; }
        public string time { get; set; }
        public string instructor { get; set; }
        public int units { get; set; }
        public string pre_reqs { get; set; }
        public string co_reqs { get; set; }
        public string start_date { get; set; }
        public string end_date { get; set; }
        public bool gen_ed { get; set; }
    }

    public class RootObject
    {
        public List<Course> courses { get; set; }
    }
}