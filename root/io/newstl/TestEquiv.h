bool IsEquiv(const std::string &, float orig, float copy)   { return IsEquiv(orig,copy); }
bool IsEquiv(const std::string &, double orig, double copy) { return IsEquiv(orig,copy); }
bool IsEquiv(const std::string &, int orig, int copy)       { return orig==copy; }
bool IsEquiv(const std::string &, UInt_t orig, UInt_t copy) { return orig==copy; }
bool IsEquiv(const std::string &, short orig, short copy)   { return orig==copy; }
bool IsEquiv(const std::string &, char orig, char copy)     { return orig==copy; }
bool IsEquiv(const std::string &, bool orig, bool copy)     { return orig==copy; }


template <class T> bool IsEquiv(const std::string &test, T* orig, T* copy);
template <class T> bool IsEquiv(const std::string &test, const T& orig, const T& copy);


template <class F, class S> bool IsEquiv(const std::string &test,
                                         const std::pair<F,S> &orig, const std::pair<F,S> &copy) {
   return IsEquiv(test, orig.first, copy.first)
      && IsEquiv(test, orig.second, copy.second);
}

template <class T> bool IsEquiv(const std::string &test, T* orig, T* copy) {
   TClass *cl = gROOT->GetClass(typeid(T));
   const char* classname = cl?cl->GetName():typeid(T).name();

   if ( (orig==0 && copy) || (orig && copy==0) ) {
      TestError(test,Form("For %s, non-initialized pointer %p %p",classname,orig,copy));
      return false;
   }
   return IsEquiv(test, *orig, *copy);
}

template <class T> bool IsEquiv(const std::string &test, const T& orig, const T& copy) {
   TClass *cl = gROOT->GetClass(typeid(T));
   const char* classname = cl?cl->GetName():typeid(T).name();

   if (orig.size() != copy.size()) {
      TestError(test,Form("For %s, wrong size! Wrote %d and read %d\n",classname,orig.size(),copy.size()));
      // return false;
   }

   bool result = true;
   typename T::const_iterator iorig = orig.begin();
   typename T::const_iterator icopy = copy.begin();
   UInt_t i = 0;
   while ( iorig != orig.end() && icopy != copy.end() ) {
      if (!IsEquiv(test,*iorig,*icopy)) {
         TestError(test, Form("for %s elem #%d are not equal",
                              classname,i));
         TestError(test,*iorig,*icopy);
         result = false;
      } else if (DebugTest()&TestDebug::kValues) {
         std::stringstream s;
         s << "(Debugging test) " << test << " elem #" << i; // << std::ends;
         TestError(s.str(),*iorig,*icopy);
      }
      i++;
      iorig++;
      icopy++;
   }
   return result;
}

bool IsEquiv(const std::string &, const EHelper &orig, const EHelper &copy) { return  orig == copy; }
bool IsEquiv(const std::string &, const Helper &orig, const Helper &copy) { return  orig.IsEquiv(copy); }
bool IsEquiv(const std::string &, const HelperClassDef &orig, const HelperClassDef &copy) { return  orig.IsEquiv(copy); }
bool IsEquiv(const std::string &, const nonvirtHelper &orig, const nonvirtHelper &copy) { return  orig.IsEquiv(copy); }
bool IsEquiv(const std::string &, const THelper &orig, const THelper &copy) { return  orig.IsEquiv(copy); }

template <class T> bool IsEquiv(const std::string &test, const GHelper<T> &orig, const GHelper<T> &copy) {
   return IsEquiv(test,orig.val,copy.val);
}

bool IsEquiv(const std::string &, const std::string& orig, const std::string& copy) {
   return orig==copy;
}

bool IsEquiv(const std::string &, const TString& orig, const TString& copy) {
   return orig==copy;
}

bool IsEquiv(const std::string &, const TNamed& orig, const TNamed& copy) {
   TString name  = orig.GetName();
   TString title = orig.GetTitle();
   return name==copy.GetName() && title==copy.GetTitle();
}


