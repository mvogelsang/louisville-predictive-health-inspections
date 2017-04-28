using LouisvilleHealthInspections.DataContext;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace LouisvilleHealthInspections.Controllers
{
    public class HealthInspectionsController : Controller
    {
        // GET: HealthInspections
        [Authorize]
        public ActionResult Index()
        {
            GetJsonData var = new GetJsonData();
            var jsonstring = var.GetData(System.Configuration.ConfigurationManager.AppSettings["GetEstablishmentsJsonString"]);
            var model = new Establishments();
            model.establishments = new List<Establishment>();
            if (jsonstring.Equals("File Not Found"))
            {
                ViewBag.FileNotFound = true;
            }
            else
            {
                model = JsonConvert.DeserializeObject<Establishments>(jsonstring);
            }
            return View(model.establishments);
        }
    }
}