import {
  Box,
  Flex,
  Button,
  HStack,
  Heading,
} from "@chakra-ui/react";
import { useLocation } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  const location = useLocation();

  return (
    <Box className="navbar-container">
      <Flex className="navbar-main">
        <HStack spacing={8} alignItems="center">
          <Heading className="navbar-title">CargoPrism Dashboard</Heading>
        </HStack>

        <Flex alignItems="center">
          <HStack className="nav-links">
            <Button variant="ghost" className={`nav-button ${location.pathname === '/' ? 'active' : ''}`}>
              <a href="/">Overview</a>
            </Button>
            <Button variant="ghost" className={`nav-button ${location.pathname === '/metrics' ? 'active' : ''}`}>
              <a href="/metrics">Performance</a>
            </Button>
            <Button variant="ghost" className={`nav-button ${location.pathname === '/market' ? 'active' : ''}`}>
              <a href="/market">Market Analysis</a>
            </Button>
            <Button variant="ghost" className={`nav-button ${location.pathname === '/alerts' ? 'active' : ''}`}>
              <a href="/alerts">Alerts</a>
            </Button>
          </HStack>
        </Flex>
      </Flex>
    </Box>
  );
}