using LouisvilleHealthInspections.DataContext;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace LouisvilleHealthInspections.Controllers
{
    public class SocialMediaComplaintsController : Controller
    {
        // GET: SocialMediaComplaints
        [Authorize]
        public ActionResult Index()
        {
            GetJsonData var = new GetJsonData();
            var jsonstring = var.GetData(System.Configuration.ConfigurationManager.AppSettings["GetTweetsJsonString"]);
            var model = new Tweets();
            model.tweets = new List<Tweet>();
            if (jsonstring.Equals("File Not Found"))
            {
                ViewBag.FileNotFound = true;
            }
            else
            {
                model = JsonConvert.DeserializeObject<Tweets>(jsonstring);
            }
            return View(model.tweets);
        }
    }
}