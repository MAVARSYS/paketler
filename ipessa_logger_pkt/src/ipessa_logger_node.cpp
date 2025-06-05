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


std::string topic_ismi = "/parsed_nmea_data";
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
    RCLCPP_INFO(this->get_logger(), "Topic ismi : %s", topic_ismi.c_str());


    subscription_ = this->create_subscription<std_msgs::msg::String>
    (
      topic_ismi, 10, std::bind(&logger_classi::logger_callback, this, std::placeholders::_1)
    );
  }

  ~logger_classi() 
  {
    if (log_file_.is_open())
    {
      log_file_.close();
    }
  }

private:

  void logger_callback(const std_msgs::msg::String::SharedPtr msg)
  {
    /* Dinlenilen node dan topic e her veri basildiginde bu calisir...*/

    // RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str());

    log_file_ << msg->data << "\n";
  }

  std::ofstream log_file_;

  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
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
