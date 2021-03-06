// Generated by gencpp from file way_point_wamv/add_way_point.msg
// DO NOT EDIT!


#ifndef WAY_POINT_WAMV_MESSAGE_ADD_WAY_POINT_H
#define WAY_POINT_WAMV_MESSAGE_ADD_WAY_POINT_H

#include <ros/service_traits.h>


#include <way_point_wamv/add_way_pointRequest.h>
#include <way_point_wamv/add_way_pointResponse.h>


namespace way_point_wamv
{

struct add_way_point
{

typedef add_way_pointRequest Request;
typedef add_way_pointResponse Response;
Request request;
Response response;

typedef Request RequestType;
typedef Response ResponseType;

}; // struct add_way_point
} // namespace way_point_wamv


namespace ros
{
namespace service_traits
{


template<>
struct MD5Sum< ::way_point_wamv::add_way_point > {
  static const char* value()
  {
    return "8f7e4b30056b33ab373baed5e3088955";
  }

  static const char* value(const ::way_point_wamv::add_way_point&) { return value(); }
};

template<>
struct DataType< ::way_point_wamv::add_way_point > {
  static const char* value()
  {
    return "way_point_wamv/add_way_point";
  }

  static const char* value(const ::way_point_wamv::add_way_point&) { return value(); }
};


// service_traits::MD5Sum< ::way_point_wamv::add_way_pointRequest> should match 
// service_traits::MD5Sum< ::way_point_wamv::add_way_point > 
template<>
struct MD5Sum< ::way_point_wamv::add_way_pointRequest>
{
  static const char* value()
  {
    return MD5Sum< ::way_point_wamv::add_way_point >::value();
  }
  static const char* value(const ::way_point_wamv::add_way_pointRequest&)
  {
    return value();
  }
};

// service_traits::DataType< ::way_point_wamv::add_way_pointRequest> should match 
// service_traits::DataType< ::way_point_wamv::add_way_point > 
template<>
struct DataType< ::way_point_wamv::add_way_pointRequest>
{
  static const char* value()
  {
    return DataType< ::way_point_wamv::add_way_point >::value();
  }
  static const char* value(const ::way_point_wamv::add_way_pointRequest&)
  {
    return value();
  }
};

// service_traits::MD5Sum< ::way_point_wamv::add_way_pointResponse> should match 
// service_traits::MD5Sum< ::way_point_wamv::add_way_point > 
template<>
struct MD5Sum< ::way_point_wamv::add_way_pointResponse>
{
  static const char* value()
  {
    return MD5Sum< ::way_point_wamv::add_way_point >::value();
  }
  static const char* value(const ::way_point_wamv::add_way_pointResponse&)
  {
    return value();
  }
};

// service_traits::DataType< ::way_point_wamv::add_way_pointResponse> should match 
// service_traits::DataType< ::way_point_wamv::add_way_point > 
template<>
struct DataType< ::way_point_wamv::add_way_pointResponse>
{
  static const char* value()
  {
    return DataType< ::way_point_wamv::add_way_point >::value();
  }
  static const char* value(const ::way_point_wamv::add_way_pointResponse&)
  {
    return value();
  }
};

} // namespace service_traits
} // namespace ros

#endif // WAY_POINT_WAMV_MESSAGE_ADD_WAY_POINT_H
