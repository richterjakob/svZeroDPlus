

#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <fstream>

#include "helpers/debug.hpp"
#include "helpers/endswith.hpp"
#include "io/jsonhandler.hpp"
#include "model/model.hpp"

#include <nlohmann/json.hpp>

// Setting scalar type to double
typedef double T;

int main(int argc, char *argv[]) {
  DEBUG_MSG("Starting svZeroDCalibrator");

  // Get input and output file name
  if (argc != 3) {
    std::cout << "Usage: calibrator path/to/config.json path/to/output.csv"
              << std::endl;
    exit(1);
  }
  std::string input_file = argv[1];
  std::string output_file = argv[2];

  std::ifstream input_file_stream(input_file);
  std::stringstream buffer;
  buffer << input_file_stream.rdbuf();
  std::string config = buffer.str();

  std::ifstream input_file_stream2(input_file);
  nlohmann::json output_config = nlohmann::json::parse(input_file_stream2);

  // Load model and configuration
  DEBUG_MSG("Read configuration");
  auto handler = IO::JsonHandler(config);

  auto model = new MODEL::Model<T>();
  std::vector<std::tuple<std::string, std::string>> connections;
  std::vector<std::tuple<std::string, std::string>> inlet_connections;
  std::vector<std::tuple<std::string, std::string>> outlet_connections;


  auto calibration_parameters = handler["calibration_parameters"];
  bool calibrate_stenosis = calibration_parameters.get_bool("calibrate_stenosis_coefficient");
  bool zero_capacitance = calibration_parameters.get_bool("set_capacitance_to_zero");

  int num_params = 3;
  if (calibrate_stenosis){
    int num_params = 4;
  }

  // Create vessels
  DEBUG_MSG("Load vessels");
  std::map<std::int64_t, std::string> vessel_id_map;
  auto vessels = handler["vessels"];
  int param_counter = 0;
  for (size_t i = 0; i < vessels.length(); i++) {
    auto vessel_config = vessels[i];
    std::string vessel_name = vessel_config.get_string("vessel_name");
    vessel_id_map.insert({vessel_config.get_int("vessel_id"), vessel_name});
    std::vector<int> param_ids;
    for (size_t k = 0; k < num_params; k++)
    {
        param_ids.push_back(param_counter++);
    }
    model->add_block(MODEL::BlockType::BLOODVESSEL,
                     param_ids,
                     vessel_name);
    DEBUG_MSG("Created vessel " << vessel_name);

    // Read connected boundary conditions
    if (vessel_config.has_key("boundary_conditions")) {
      auto vessel_bc_config = vessel_config["boundary_conditions"];
      if (vessel_bc_config.has_key("inlet")) {
        inlet_connections.push_back(
            {vessel_bc_config.get_string("inlet"), vessel_name});
      }
      if (vessel_bc_config.has_key("outlet")) {
        outlet_connections.push_back(
            {vessel_name, vessel_bc_config.get_string("outlet")});
      }
    }
  }

  // Create junctions
  auto junctions = handler["junctions"];
  for (size_t i = 0; i < junctions.length(); i++) {
    auto junction_config = junctions[i];
    auto junction_name = junction_config.get_string("junction_name");
    auto outlet_vessels = junction_config.get_int_array("outlet_vessels");
    int num_outlets = outlet_vessels.size();
    if (num_outlets == 1) {
      model->add_block(MODEL::BlockType::JUNCTION, {}, junction_name);
    } else {
      std::vector<int> param_ids;
      for (size_t i = 0; i < (num_outlets * num_params); i++) {
        param_ids.push_back(param_counter++);
      }
      model->add_block(MODEL::BlockType::BLOODVESSELJUNCTION, param_ids,
                       junction_name);
    }
    // Check for connections to inlet and outlet vessels and append to
    // connections list
    for (auto vessel_id : junction_config.get_int_array("inlet_vessels")) {
      connections.push_back({vessel_id_map[vessel_id], junction_name});
    }
    for (auto vessel_id : junction_config.get_int_array("outlet_vessels")) {
      connections.push_back({junction_name, vessel_id_map[vessel_id]});
    }
    DEBUG_MSG("Created junction " << junction_name);
  }

  // Create Connections
  DEBUG_MSG("Created connection");
  for (auto &connection : connections) {
    auto ele1 = model->get_block(std::get<0>(connection));
    auto ele2 = model->get_block(std::get<1>(connection));
    model->add_node({ele1}, {ele2}, ele1->get_name() + ":" + ele2->get_name());
  }

  for (auto &connection : inlet_connections) {
    auto ele = model->get_block(std::get<1>(connection));
    model->add_node({}, {ele}, static_cast<std::string>(std::get<0>(connection)) + ":" + ele->get_name());
  }

  for (auto &connection : outlet_connections) {
    auto ele = model->get_block(std::get<0>(connection));
    model->add_node({ele}, {}, ele->get_name() + ":" + static_cast<std::string>(std::get<1>(connection)));
  }

  model->finalize();

  for (size_t i = 0; i < model->dofhandler.size(); i++) {
    std::string var_name = model->dofhandler.variables[i];
    DEBUG_MSG("Variable " << i << ": " << var_name);
  }

  DEBUG_MSG("Number of parameters " << param_counter);

  DEBUG_MSG("Reading observations");
  std::vector<std::vector<T>> y_all;
  std::vector<std::vector<T>> dy_all;
  auto y_values = handler["y"];
  auto dy_values = handler["dy"];
  for (size_t i = 0; i < model->dofhandler.size(); i++) {
    std::string var_name = model->dofhandler.variables[i];
    DEBUG_MSG("Reading y values for variable " << var_name);
    y_all.push_back(y_values.get_double_array(var_name));
    DEBUG_MSG("Reading dy values for variable " << var_name);
    dy_all.push_back(dy_values.get_double_array(var_name));
  }

  int num_observations = y_all[0].size();
  DEBUG_MSG("Number of observations: " << num_observations);

  int num_dofs = model->dofhandler.size();
  int max_nliter = 100;

  // =====================================
  // Setup alpha
  // =====================================
  Eigen::Matrix<T, Eigen::Dynamic, 1> alpha =
      Eigen::Matrix<T, Eigen::Dynamic, 1>::Zero(param_counter);
  DEBUG_MSG("Reading initial alpha");
  for (auto &vessel_config : output_config["vessels"])
  {
    std::string vessel_name = vessel_config["vessel_name"];
    DEBUG_MSG("Reading initial alpha for " << vessel_name);
    auto block = model->get_block(vessel_name);
    alpha[block->global_param_ids[0]] = vessel_config["zero_d_element_values"].value("R_poiseuille", 0.0);
    alpha[block->global_param_ids[1]] = vessel_config["zero_d_element_values"].value("C", 0.0);
    alpha[block->global_param_ids[2]] = vessel_config["zero_d_element_values"].value("L", 0.0);
    if (num_params > 3)
    {
      alpha[block->global_param_ids[3]] = vessel_config["zero_d_element_values"].value("stenosis_coefficient", 0.0);
    }
  }
  for (auto &junction_config : output_config["junctions"])
  {

    std::string junction_name = junction_config["junction_name"];
    DEBUG_MSG("Reading initial alpha for " << junction_name);
    auto block = model->get_block(junction_name);
    int num_outlets = block->outlet_nodes.size();

    if (num_outlets < 2)
    {
        continue;
    }

    for (size_t i = 0; i < num_outlets; i++)
    {
        alpha[block->global_param_ids[i]] = 0.0;
        alpha[block->global_param_ids[i+num_outlets]] = 0.0;
        alpha[block->global_param_ids[i+2*num_outlets]] = 0.0;
        if (num_params > 3) {
          alpha[block->global_param_ids[i+3*num_outlets]] = 0.0;
        }
    }
  }


  // =====================================
  // Gauss-Newton
  // =====================================
  DEBUG_MSG("Starting Gauss-Newton");
  Eigen::SparseMatrix<T> jacobian = Eigen::SparseMatrix<T>(
      num_observations * model->dofhandler.size(), param_counter);
  Eigen::Matrix<T, Eigen::Dynamic, 1> residual =
      Eigen::Matrix<T, Eigen::Dynamic, 1>::Zero(num_observations *
                                                model->dofhandler.size());

  for (size_t nliter = 0; nliter < max_nliter; nliter++)
  {
    std::cout << "Gauss-Newton Iteration " << nliter << std::endl;
    for (size_t i = 0; i < num_observations; i++) {
      Eigen::Matrix<T, Eigen::Dynamic, 1> y =
          Eigen::Matrix<T, Eigen::Dynamic, 1>::Zero(model->dofhandler.size());
      Eigen::Matrix<T, Eigen::Dynamic, 1> dy =
          Eigen::Matrix<T, Eigen::Dynamic, 1>::Zero(model->dofhandler.size());
      for (size_t k = 0; k < model->dofhandler.size(); k++) {
        y(k) = y_all[k][i];
        dy(k) = dy_all[k][i];
      }

      for (size_t j = 0; j < model->get_num_blocks(true); j++)
      {  
        auto block = model->get_block(j);
        block->update_gradient(jacobian, residual, alpha, y, dy);

        for (size_t l = 0; l < block->global_eqn_ids.size(); l++) {
          block->global_eqn_ids[l] += num_dofs;
        }
      }
    }

    for (size_t j = 0; j < model->get_num_blocks(true); j++)
      {  
        auto block = model->get_block(j);
      for (size_t l = 0; l < block->global_eqn_ids.size(); l++) {
          block->global_eqn_ids[l] -= num_dofs * num_observations;
        }
    }

    Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic> mat = jacobian.transpose() * jacobian;
    Eigen::Matrix<T, Eigen::Dynamic, 1> new_alpha = alpha - mat.inverse() * jacobian.transpose() * residual;

    Eigen::Matrix<T, Eigen::Dynamic, 1> diff = new_alpha - alpha;

    T residual_norm = 0.0;
    for (size_t i = 0; i < param_counter; i++)
    {
      residual_norm += diff[i] * diff[i];
    }
    residual_norm = pow(residual_norm, 0.5);
    std::cout << "residual norm: " << residual_norm << std::endl;

    alpha = new_alpha;

    if (residual_norm < 1e-10) break;

  }

  // =====================================
  // Write output
  // =====================================
  for (auto &vessel_config : output_config["vessels"])
  {
    std::string vessel_name = vessel_config["vessel_name"];
    auto block = model->get_block(vessel_name);
    T stenosis_coeff = 0.0;
    if (num_params > 3)
    {
      stenosis_coeff = alpha[block->global_param_ids[3]];
    }
    T c_value = 0.0;
    if (!zero_capacitance)
    {
      c_value = alpha[block->global_param_ids[1]];
    }
    vessel_config["zero_d_element_values"] = {
        {"R_poiseuille", alpha[block->global_param_ids[0]]},
        {"C", c_value},
        {"L", alpha[block->global_param_ids[2]]},
        {"stenosis_coefficient", stenosis_coeff}
    };
  }

  for (auto &junction_config : output_config["junctions"])
  {

    std::string junction_name = junction_config["junction_name"];
    auto block = model->get_block(junction_name);
    int num_outlets = block->outlet_nodes.size();

    if (num_outlets < 2)
    {
        continue;
    }

    std::vector<T> r_values;
    for (size_t i = 0; i < num_outlets; i++)
    {
        r_values.push_back(alpha[block->global_param_ids[i]]);
    }
    std::vector<T> c_values;
    if (zero_capacitance)
    {
      for (size_t i = 0; i < num_outlets; i++)
      {
          c_values.push_back(0.0);
      }
    }
    else {
      for (size_t i = 0; i < num_outlets; i++)
      {
          c_values.push_back(alpha[block->global_param_ids[i+num_outlets]]);
      }
    }
    std::vector<T> l_values;
    for (size_t i = 0; i < num_outlets; i++)
    {
        l_values.push_back(alpha[block->global_param_ids[i+2*num_outlets]]);
    }
    std::vector<T> ste_values;
    if (num_params > 3)
    {
        for (size_t i = 0; i < num_outlets; i++){
          ste_values.push_back(alpha[block->global_param_ids[i+3*num_outlets]]);
        }
    }
    else {
      for (size_t i = 0; i < num_outlets; i++)
      {
          ste_values.push_back(0.0);
      }
    }
    junction_config["junction_type"] = "BloodVesselJunction";
    junction_config["junction_values"] = {
        {"R_poiseuille", r_values},
        {"C", c_values},
        {"L", l_values},
        {"stenosis_coefficient", ste_values}
    };
  }

  output_config.erase("y");
  output_config.erase("dy");
  output_config.erase("calibration_parameters");

  std::ofstream o(output_file);
  o << std::setw(4) << output_config << std::endl;
}
