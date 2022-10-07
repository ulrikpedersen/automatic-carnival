/*----- PROTECTED REGION ID(PipeServerClass.h) ENABLED START -----*/
//=============================================================================
//
// file :        PipeServerClass.h
//
// description : Include for the PipeServer root class.
//               This class is the singleton class for
//                the PipeServer device class.
//               It contains all properties and methods which the 
//               PipeServer requires only once e.g. the commands.
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


#ifndef PipeServerClass_H
#define PipeServerClass_H

#include <tango/tango.h>
#include <PipeServer.h>


/*----- PROTECTED REGION END -----*/	//	PipeServerClass.h


namespace PipeServer_ns
{
/*----- PROTECTED REGION ID(PipeServerClass::classes for dynamic creation) ENABLED START -----*/


/*----- PROTECTED REGION END -----*/	//	PipeServerClass::classes for dynamic creation

//=========================================
//	Define classes for pipes
//=========================================
//	Pipe TestPipe class definition
class TestPipeClass: public Tango::WPipe
{
public:
	TestPipeClass(const std::string &name, Tango::DispLevel level)
		:WPipe(name, level) {};

	~TestPipeClass() {};

	virtual bool is_allowed (Tango::DeviceImpl *dev,Tango::PipeReqType _prt)
		{return (static_cast<PipeServer *>(dev))->is_TestPipe_allowed(_prt);}
	virtual void read(Tango::DeviceImpl *dev)
		{(static_cast<PipeServer *>(dev))->read_TestPipe(*this);}
	virtual void write(Tango::DeviceImpl *dev)
		{(static_cast<PipeServer *>(dev))->write_TestPipe(*this);}
};


//=========================================
//	Define classes for commands
//=========================================
//	Command cmd_push_pipe_event class definition
class cmd_push_pipe_eventClass : public Tango::Command
{
public:
	cmd_push_pipe_eventClass(const char   *name,
	               Tango::CmdArgType in,
				   Tango::CmdArgType out,
				   const char        *in_desc,
				   const char        *out_desc,
				   Tango::DispLevel  level)
	:Command(name,in,out,in_desc,out_desc, level)	{};

	cmd_push_pipe_eventClass(const char   *name,
	               Tango::CmdArgType in,
				   Tango::CmdArgType out)
	:Command(name,in,out)	{};
	~cmd_push_pipe_eventClass() {};
	
	virtual CORBA::Any *execute (Tango::DeviceImpl *dev, const CORBA::Any &any);
	virtual bool is_allowed (Tango::DeviceImpl *dev, const CORBA::Any &any)
	{return (static_cast<PipeServer *>(dev))->is_cmd_push_pipe_event_allowed(any);}
};


/**
 *	The PipeServerClass singleton definition
 */

#ifdef _TG_WINDOWS_
class __declspec(dllexport)  PipeServerClass : public Tango::DeviceClass
#else
class PipeServerClass : public Tango::DeviceClass
#endif
{
	/*----- PROTECTED REGION ID(PipeServerClass::Additionnal DServer data members) ENABLED START -----*/
	
	
	/*----- PROTECTED REGION END -----*/	//	PipeServerClass::Additionnal DServer data members

	public:
		//	write class properties data members
		Tango::DbData	cl_prop;
		Tango::DbData	cl_def_prop;
		Tango::DbData	dev_def_prop;
	
		//	Method prototypes
		static PipeServerClass *init(const char *);
		static PipeServerClass *instance();
		~PipeServerClass();
		Tango::DbDatum	get_class_property(std::string &);
		Tango::DbDatum	get_default_device_property(std::string &);
		Tango::DbDatum	get_default_class_property(std::string &);
	
	protected:
		PipeServerClass(std::string &);
		static PipeServerClass *_instance;
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

#endif   //	PipeServer_H
