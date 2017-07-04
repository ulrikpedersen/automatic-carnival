/*----- PROTECTED REGION ID(IfchangeServer.h) ENABLED START -----*/
//=============================================================================
//
// file :        IfchangeServer.h
//
// description : Include file for the IfchangeServer class
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


#ifndef IfchangeServer_H
#define IfchangeServer_H

#include <tango.h>


/*----- PROTECTED REGION END -----*/	//	IfchangeServer.h

/**
 *  IfchangeServer class description:
 *    
 */

namespace IfchangeServer_ns
{
/*----- PROTECTED REGION ID(IfchangeServer::Additional Class Declarations) ENABLED START -----*/

//	Additional Class Declarations

/*----- PROTECTED REGION END -----*/	//	IfchangeServer::Additional Class Declarations

class IfchangeServer : public TANGO_BASE_CLASS
{

/*----- PROTECTED REGION ID(IfchangeServer::Data Members) ENABLED START -----*/

//	Add your own data members

/*----- PROTECTED REGION END -----*/	//	IfchangeServer::Data Members


//	Attribute data members
public:
	Tango::DevBoolean	*attr_busy_read;

//	Constructors and destructors
public:
	/**
	 * Constructs a newly device object.
	 *
	 *	@param cl	Class.
	 *	@param s 	Device Name
	 */
	IfchangeServer(Tango::DeviceClass *cl,string &s);
	/**
	 * Constructs a newly device object.
	 *
	 *	@param cl	Class.
	 *	@param s 	Device Name
	 */
	IfchangeServer(Tango::DeviceClass *cl,const char *s);
	/**
	 * Constructs a newly device object.
	 *
	 *	@param cl	Class.
	 *	@param s 	Device name
	 *	@param d	Device description.
	 */
	IfchangeServer(Tango::DeviceClass *cl,const char *s,const char *d);
	/**
	 * The device object destructor.
	 */
	~IfchangeServer() {delete_device();};


//	Miscellaneous methods
public:
	/*
	 *	will be called at device destruction or at init command.
	 */
	void delete_device();
	/*
	 *	Initialize the device
	 */
	virtual void init_device();
	/*
	 *	Always executed method before execution command method.
	 */
	virtual void always_executed_hook();


//	Attribute methods
public:
	//--------------------------------------------------------
	/*
	 *	Method      : IfchangeServer::read_attr_hardware()
	 *	Description : Hardware acquisition for attributes.
	 */
	//--------------------------------------------------------
	virtual void read_attr_hardware(vector<long> &attr_list);

/**
 *	Attribute busy related methods
 *	Description: 
 *
 *	Data type:	Tango::DevBoolean
 *	Attr type:	Scalar
 */
	virtual void read_busy(Tango::Attribute &attr);
	virtual bool is_busy_allowed(Tango::AttReqType type);

//	Dynamic attribute methods
public:

	/**
	 *	Attribute ioattr related methods
	 *	Description: 
	 *
	 *	Data type:	Tango::DevDouble
	 *	Attr type:	Scalar
	 */
	virtual void read_ioattr(Tango::Attribute &attr);
	virtual bool is_ioattr_allowed(Tango::AttReqType type);
	void add_ioattr_dynamic_attribute(string attname);
	void remove_ioattr_dynamic_attribute(string attname);
	Tango::DevDouble *get_ioattr_data_ptr(string &name);
	map<string,Tango::DevDouble>	   ioattr_data;

	//--------------------------------------------------------
	/**
	 *	Method      : IfchangeServer::add_dynamic_attributes()
	 *	Description : Add dynamic attributes if any.
	 */
	//--------------------------------------------------------
	void add_dynamic_attributes();




//	Command related methods
public:
	/**
	 *	Command Add_dynamic related method
	 *	Description: 
	 *
	 */
	virtual void add_dynamic();
	virtual bool is_Add_dynamic_allowed(const CORBA::Any &any);
	/**
	 *	Command Delete_Dynamic related method
	 *	Description: 
	 *
	 */
	virtual void delete__dynamic();
	virtual bool is_Delete_Dynamic_allowed(const CORBA::Any &any);

//	Dynamic commands methods
public:
	/**
	 *	Command iocmd related method
	 *	Description: 
	 *
	 */
	virtual void iocmd(Tango::Command &command);
	virtual bool is_iocmd_allowed(const CORBA::Any &any);
	void add_iocmd_dynamic_command(string cmdname, bool device);
	void remove_iocmd_dynamic_command(string cmdname);

	//--------------------------------------------------------
	/**
	 *	Method      : IfchangeServer::add_dynamic_commands()
	 *	Description : Add dynamic commands if any.
	 */
	//--------------------------------------------------------
	void add_dynamic_commands();

/*----- PROTECTED REGION ID(IfchangeServer::Additional Method prototypes) ENABLED START -----*/

//	Additional Method prototypes

/*----- PROTECTED REGION END -----*/	//	IfchangeServer::Additional Method prototypes
};

/*----- PROTECTED REGION ID(IfchangeServer::Additional Classes Definitions) ENABLED START -----*/

//	Additional Classes Definitions

/*----- PROTECTED REGION END -----*/	//	IfchangeServer::Additional Classes Definitions

}	//	End of namespace

#endif   //	IfchangeServer_H