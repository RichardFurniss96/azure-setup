# Create a resource group
resource "azurerm_resource_group" "rf-test" {
  name     = "rftest"
  location = "UK South"
}

