using LouisvilleHealthInspections.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using System.Web.Security;

namespace LouisvilleHealthInspections.Controllers
{
    public class AccountController : Controller
    {
        // GET: /Account/

        public ActionResult Index()
        {
            return RedirectToAction("Login");
        }

        public ActionResult Login()
        {
            return View("Login");
        }

        [HttpPost]
        public ActionResult Login(LoginViewModel login)
        {
            if (!ModelState.IsValid)
            {
                ViewBag.Error = "Form is not valid; please review and try again.";
                return View("Login");
            }

            if (login.Username == System.Configuration.ConfigurationManager.AppSettings["UserName"] && login.Password == System.Configuration.ConfigurationManager.AppSettings["Password"])
                FormsAuthentication.RedirectFromLoginPage(login.Username, true);

            ViewBag.Error = "Credentials invalid. Please try again.";
            return View("Login");
        }

        public ActionResult Logout()
        {
            Session.Clear();
            FormsAuthentication.SignOut();
            return RedirectToAction("Index", "Home");
        }
    }
}