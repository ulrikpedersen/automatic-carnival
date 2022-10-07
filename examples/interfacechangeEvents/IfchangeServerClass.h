/*----- PROTECTED REGION ID(IfchangeServerClass.h) ENABLED START -----*/
//=============================================================================
//
// file :        IfchangeServerClass.h
//
// description : Include for the IfchangeServer root class.
//               This class is the singleton class for
//                the IfchangeServer device class.
//               It contains all properties and methods which the 
//               IfchangeServer requires only once e.g. the commands.
//
// project :     
//
// This file is part of Tango device class.
// 
// Tango is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// Tango is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with Tango.  If not, see <http://www.gnu.org/licenses/>.
// 
// $Author:  $
//
// $Revision:  $
// $Date:  $
//
// $HeadURL:  $
//
//=============================================================================
//                This file is generated by POGO
//        (Program Obviously used to Generate tango Object)
//=============================================================================


#ifndef IfchangeServerClass_H
#define IfchangeServerClass_H

#include <tango/tango.h>
#include <IfchangeServer.h>


/*----- PROTECTED REGION END -----*/	//	IfchangeServerClass.h


namespace IfchangeServer_ns
{
/*----- PROTECTED REGION ID(IfchangeServerClass::classes for dynamic creation) ENABLED START -----*/


/*----- PROTECTED REGION END -----*/	//	IfchangeServerClass::classes for dynamic creation

//=========================================
//	Define classes for attributes
//=========================================
//	Attribute busy class definition
class busyAttrib: public Tango::Attr
{
public:
	busyAttrib():Attr("busy",
			Tango::DEV_BOOLEAN, Tango::READ) {};
	~busyAttrib() {};
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
		{(static_cast<IfchangeServer *>(dev))->read_busy(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
		{return (static_cast<IfchangeServer *>(dev))->is_busy_allowed(ty);}
};


//=========================================
//	Define classes for dynamic attributes
//=========================================
//	Attribute ioattr class definition
class ioattrAttrib: public Tango::Attr
{
public:
	ioattrAttrib(const std::string &att_name):Attr(att_name.c_str(),
			Tango::DEV_DOUBLE, Tango::READ) {};
	~ioattrAttrib() {};
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
		{(static_cast<IfchangeServer *>(dev))->read_ioattr(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
		{return (static_cast<IfchangeServer *>(dev))->is_ioattr_allowed(ty);}
};


//=========================================
//	Define classes for commands
//=========================================
//	Command Add_dynamic class definition
class Add_dynamicClass : public Tango::Command
{
public:
	Add_dynamicClass(const char   *name,
	               Tango::CmdArgType in,
				   Tango::CmdArgType out,
				   const char        *in_desc,
				   const char        *out_desc,
				   Tango::DispLevel  level)
	:Command(name,in,out,in_desc,out_desc, level)	{};

	Add_dynamicClass(const char   *name,
	               Tango::CmdArgType in,
				   Tango::CmdArgType out)
	:Command(name,in,out)	{};
	~Add_dynamicClass() {};
	
	virtual CORBA::Any *execute (Tango::DeviceImpl *dev, const CORBA::Any &any);
	virtual bool is_allowed (Tango::DeviceImpl *dev, const CORBA::Any &any)
	{return (static_cast<IfchangeServer *>(dev))->is_Add_dynamic_allowed(any);}
};

//	Command Delete_Dynamic class definition
class Delete_DynamicClass : public Tango::Command
{
public:
	Delete_DynamicClass(const char   *name,
	               Tango::CmdArgType in,
				   Tango::CmdArgType out,
				   const char        *in_desc,
				   const char        *out_desc,
				   Tango::DispLevel  level)
	:Command(name,in,out,in_desc,out_desc, level)	{};

	Delete_DynamicClass(const char   *name,
	               Tango::CmdArgType in,
				   Tango::CmdArgType out)
	:Command(name,in,out)	{};
	~Delete_DynamicClass() {};
	
	virtual CORBA::Any *execute (Tango::DeviceImpl *dev, const CORBA::Any &any);
	virtual bool is_allowed (Tango::DeviceImpl *dev, const CORBA::Any &any)
	{return (static_cast<IfchangeServer *>(dev))->is_Delete_Dynamic_allowed(any);}
};


//=========================================
//	Define classes for dynamic commands
//=========================================
//	Command iocmd class definition
class iocmdClass : public Tango::Command
{
public:
	iocmdClass(const char   *name,
	               Tango::CmdArgType in,
				   Tango::CmdArgType out,
				   const char        *in_desc,
				   const char        *out_desc,
				   Tango::DispLevel  level)
	:Command(name,in,out,in_desc,out_desc, level)	{};

	iocmdClass(const char   *name,
	               Tango::CmdArgType in,
				   Tango::CmdArgType out)
	:Command(name,in,out)	{};
	~iocmdClass() {};
	
	virtual CORBA::Any *execute (Tango::DeviceImpl *dev, const CORBA::Any &any);
	virtual bool is_allowed (Tango::DeviceImpl *dev, const CORBA::Any &any)
	{return (static_cast<IfchangeServer *>(dev))->is_iocmd_allowed(any);}
};


/**
 *	The IfchangeServerClass singleton definition
 */

#ifdef _TG_WINDOWS_
class __declspec(dllexport)  IfchangeServerClass : public Tango::DeviceClass
#else
class IfchangeServerClass : public Tango::DeviceClass
#endif
{
	/*----- PROTECTED REGION ID(IfchangeServerClass::Additionnal DServer data members) ENABLED START -----*/
	
	
	/*----- PROTECTED REGION END -----*/	//	IfchangeServerClass::Additionnal DServer data members

	public:
		//	write class properties data members
		Tango::DbData	cl_prop;
		Tango::DbData	cl_def_prop;
		Tango::DbData	dev_def_prop;
	
		//	Method prototypes
		static IfchangeServerClass *init(const char *);
		static IfchangeServerClass *instance();
		~IfchangeServerClass();
		Tango::DbDatum	get_class_property(std::string &);
		Tango::DbDatum	get_default_device_property(std::string &);
		Tango::DbDatum	get_default_class_property(std::string &);
	
	protected:
		IfchangeServerClass(std::string &);
		static IfchangeServerClass *_instance;
		void command_factory();
		void attribute_factory(std::vector<Tango::Attr *> &);
		void pipe_factory();
		void write_class_property();
		void set_default_property();
		void get_class_property();
		std::string get_cvstag();
		std::string get_cvsroot();
	
	private:
		void device_factory(const Tango::DevVarStringArray *);
		void create_static_attribute_list(std::vector<Tango::Attr *> &);
		void erase_dynamic_attributes(const Tango::DevVarStringArray *,std::vector<Tango::Attr *> &);
		std::vector<std::string>	defaultAttList;
		Tango::Attr *get_attr_object_by_name(std::vector<Tango::Attr *> &att_list, std::string attname);
};

}	//	End of namespace

#endif   //	IfchangeServer_H
