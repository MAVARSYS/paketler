#include <functional>
#include <memory>
#include <fstream>
#include <chrono>
#include <iomanip>   // std::put_time
#include <sstream>   // std::stringstream
#include <filesystem>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "ament_index_cpp/get_package_share_directory.hpp"
#include "hesai_ros_driver/msg/udp_frame.hpp"



// std::string topic_ismi_1 = "/lidar_imu";
std::string topic_ismi_2 = "/lidar_packets";
// std::string topic_ismi_3 = "/lidar_packets_loss";
// std::string topic_ismi_4 = "/lidar_points";

std::string get_timestamped_filename();


class logger_classi : public rclcpp::Node
{
public:
  logger_classi() : Node("Logger_Node")
  {

    std::string dosya_ismi_string = get_timestamped_filename();
    log_file_.open(dosya_ismi_string, std::ios::app);
    if (!log_file_.is_open()) 
    {
        RCLCPP_ERROR(this->get_logger(), "Dosya açılamadı!");
        RCLCPP_INFO(this->get_logger(), "Dosya yolu : %s", dosya_ismi_string.c_str());
        return;
    }

    RCLCPP_INFO(this->get_logger(), "Dosya açıldı...");
    RCLCPP_INFO(this->get_logger(), "Dosya yolu : %s", dosya_ismi_string.c_str());
    // RCLCPP_INFO(this->get_logger(), "Topic ismi 1 : %s", topic_ismi_1.c_str());
    RCLCPP_INFO(this->get_logger(), "Topic ismi 2 : %s", topic_ismi_2.c_str());
    // RCLCPP_INFO(this->get_logger(), "Topic ismi 3 : %s", topic_ismi_3.c_str());
    // RCLCPP_INFO(this->get_logger(), "Topic ismi 4 : %s", topic_ismi_4.c_str());



    // subscription_ = this->create_subscription<std_msgs::msg::String>
    // (
    //   topic_ismi_1, 10000, std::bind(&logger_classi::logger_callback, this, std::placeholders::_1)
    // );

        subscription_ = this->create_subscription<hesai_ros_driver::msg::UdpFrame>
    (
      topic_ismi_2, 10, std::bind(&logger_classi::logger_callback, this, std::placeholders::_1)
    );

    //     subscription_ = this->create_subscription<std_msgs::msg::String>
    // (
    //   topic_ismi_3, 10000, std::bind(&logger_classi::logger_callback, this, std::placeholders::_1)
    // );

    //     subscription_ = this->create_subscription<std_msgs::msg::String>
    // (
    //   topic_ismi_4, 10000, std::bind(&logger_classi::logger_callback, this, std::placeholders::_1)
    // );

  }

  ~logger_classi() 
  {
    if (log_file_.is_open())
    {
      log_file_.close();
    }
  }

private:

  void logger_callback(const hesai_ros_driver::msg::UdpFrame::SharedPtr msg)
  {
    /* Dinlenilen node dan topic e her veri basildiginde bu calisir...*/

    RCLCPP_INFO(this->get_logger(), "UDP Frame alındı, boyut: %ld byte", msg->data.size());

    // RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str());

    log_file_ << msg->data << "\n";
    log_file_ << msg
  }

  std::ofstream log_file_;

  rclcpp::Subscription<hesai_ros_driver::msg::UdpFrame>::SharedPtr subscription_;
};



int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<logger_classi>());
  rclcpp::shutdown();
  return 0;
}


std::string get_timestamped_filename()
{
  auto now = std::chrono::system_clock::now();
  std::time_t now_c = std::chrono::system_clock::to_time_t(now);

  std::stringstream ss;
  ss << std::put_time(std::localtime(&now_c), "ros2_log_%Y-%m-%d_%H-%M-%S.txt");
  
  std::string filename = ss.str();

  // Paketin dizinini al
  std::string dosya_yolu = __FILE__;  // kendi paket adını yaz

  dosya_yolu = std::filesystem::path(dosya_yolu).parent_path().parent_path().string();

  std::string tam_dosya_yolu = dosya_yolu + "/loglar";

  std::filesystem::create_directories(tam_dosya_yolu);

  return tam_dosya_yolu + "/" + filename;
} 
